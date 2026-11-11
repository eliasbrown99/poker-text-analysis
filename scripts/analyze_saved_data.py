"""Recalculate aggregate descriptive evidence from copies of the saved poker DBs.

Standard library only. No API clients, network requests, source imports, migrations,
or writes to the original databases. Raw records never enter published outputs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import statistics
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_snapshot(source, destination):
    """Copy DB and any WAL/SHM sidecars before connecting, even in read-only mode."""
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(source) + suffix)
        if p.exists():
            shutil.copy2(p, Path(str(destination) + suffix))
    conn = sqlite3.connect(destination.as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def table(conn, name):
    return [dict(r) for r in conn.execute('SELECT * FROM "' + name + '"')]


def merge_identical_hands(hands):
    """Merge only exact non-ID duplicates; include thread_id in the comparison.

    Retain the smallest ID and return a mapping for *all* child associations.
    Similar hand narratives and separate threads are not fuzzy-deduplicated.
    """
    signatures, retained, id_map = {}, [], {}
    for hand in sorted(hands, key=lambda h: h["id"]):
        signature = tuple(sorted((k, v) for k, v in hand.items() if k != "id"))
        if signature not in signatures:
            signatures[signature] = hand["id"]
            retained.append(hand)
        id_map[hand["id"]] = signatures[signature]
    return retained, id_map


def unique_topics(rows, bridge, id_map=None):
    """One (entity, canonical topic) pair, regardless of alias repetition."""
    pairs = set()
    for record_id, alias in rows:
        if alias not in bridge:
            raise ValueError("Unmapped topic label; review the stored bridge first")
        canonical = bridge[alias]
        if not canonical:
            raise ValueError("Empty canonical topic")
        mapped_id = id_map[record_id] if id_map is not None else record_id
        pairs.add((mapped_id, canonical))
    return pairs


def summarize_topics(pairs):
    denominator = len({record_id for record_id, _ in pairs})
    counts = Counter(topic for _, topic in pairs)
    return denominator, counts


def collapse_exact_rows(rows, id_map=None):
    """Audit exact duplication, excluding surrogate IDs and remapping hands."""
    result = set()
    for row in rows:
        values = {k: v for k, v in row.items() if k != "id"}
        if id_map is not None and "hand_id" in values:
            values["hand_id"] = id_map[values["hand_id"]]
        result.add(tuple(sorted(values.items())))
    return result


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def analyze(forum, creator):
    hands_raw = table(forum, "hands")
    hands, id_map = merge_identical_hands(hands_raw)
    tags = table(forum, "archetypes")
    videos = table(creator, "videos")
    labels = table(creator, "video_labels")
    bridge_rows = table(forum, "archetype_bridge")
    bridge = {r["alias"]: r["canonical"] for r in bridge_rows}
    if bridge != {r["alias"]: r["canonical"] for r in table(creator, "archetype_bridge")}:
        raise ValueError("The stored topic mappings disagree")
    if any(r["video_id"] not in {v["video_id"] for v in videos} for r in labels):
        raise ValueError("Orphan video label")
    hand_topics = unique_topics(((r["hand_id"], r["label"]) for r in tags), bridge, id_map)
    video_topics = unique_topics(((r["video_id"], a) for r in labels
                                  for a in json.loads(r["archetypes"] or "[]")), bridge)
    n_hands, forum_counts = summarize_topics(hand_topics)
    n_videos, video_counts = summarize_topics(video_topics)
    topic_rows = []
    for topic in sorted(forum_counts.keys() | video_counts.keys()):
        h, v = forum_counts[topic], video_counts[topic]
        topic_rows.append({"topic": topic, "hand_records": h, "tagged_hand_denominator": n_hands,
                           "hand_percent": round(100*h/n_hands, 4), "videos": v,
                           "tagged_video_denominator": n_videos, "video_percent": round(100*v/n_videos, 4)})
    advice = defaultdict(list)
    for row in labels:
        value = row["advice_density_pct"]
        if value is None:
            continue
        if not isinstance(value, (int, float)) or not 0 <= value <= 100:
            raise ValueError("Advice estimate outside 0–100")
        advice[row["segment_type"]].append(value)
    advice_rows = [{"segment_type": segment, "estimate_percent": value, "videos": n}
                   for segment in sorted(advice)
                   for value, n in sorted(Counter(advice[segment]).items())]
    advice_summary = [{"segment_type": segment, "videos": len(vals),
                       "median_estimate": statistics.median(vals),
                       "minimum_estimate": min(vals), "maximum_estimate": max(vals)}
                      for segment, vals in sorted(advice.items(), key=lambda item: -len(item[1]))]
    replies = table(forum, "replies")
    streets = table(forum, "street_metrics")
    players = table(forum, "players")
    threads = table(forum, "threads")
    raw_comment_count = sum(len(json.loads(t["replies"] or "[]")) for t in threads)
    coverage = {name: len({id_map[r["hand_id"]] for r in rows})
                for name, rows in (("with_players", players), ("with_topics", tags),
                                   ("with_replies", replies), ("with_street_metrics", streets))}
    original_join_count = forum.execute("""SELECT COUNT(*) FROM hands h
        JOIN archetypes a ON a.hand_id=h.id JOIN archetype_bridge b ON b.alias=a.label
        LEFT JOIN replies r ON r.hand_id=h.id""").fetchone()[0]
    summary = {
        "edition": "November 2026 descriptive reanalysis of saved May 2025 extraction",
        "threads": len(threads), "threads_with_hand_records": len({h["thread_id"] for h in hands}),
        "source_reply_entries": raw_comment_count,
        "stored_hand_records": len(hands_raw), "distinct_hand_records": len(hands),
        "exact_duplicate_hand_records_removed": len(hands_raw)-len(hands),
        "tagged_hand_records": n_hands, "hand_topic_pairs": len(hand_topics),
        "stored_player_records": len(players), "canonical_topics": len(set(bridge.values())),
        "aliases": len(bridge), "videos_collected": len(videos), "videos_labeled": len(labels),
        "videos_tagged": n_videos, "video_topic_pairs": len(video_topics),
        "shared_topics": len(forum_counts.keys() & video_counts.keys()),
        "creator_count": len({v["creator"] for v in videos}),
        "segment_counts": dict(Counter(r["segment_type"] for r in labels)),
        "advice_summary": advice_summary, "hand_coverage": coverage,
        "stored_replies": len(replies), "distinct_reply_tuples": len(collapse_exact_rows(replies, id_map)),
        "stored_street_metrics": len(streets), "distinct_street_tuples": len(collapse_exact_rows(streets, id_map)),
        "original_forum_join_rows": original_join_count,
        "notes": ["Topics and advice estimates are model-generated labels, not human-validated measurements.",
                  "Prevalence denominators include only records with at least one mapped topic.",
                  "Multiple topics per record; percentages do not sum to 100.",
                  "No reply or player join is used to count hand-topic pairs.",
                  "Distinct tuples are an audit diagnostic, not a recovered count of real comments or betting events.",
                  "No model inference, source repair, scraping, or causal inference was performed."]
    }
    for name, conn in (("forum", forum), ("creator", creator)):
        if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError(name + " failed integrity check")
        if conn.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError(name + " contains orphan keys")
    assert sum(forum_counts.values()) == len(hand_topics)
    assert sum(video_counts.values()) == len(video_topics)
    assert all(0 <= r["hand_percent"] <= 100 and 0 <= r["video_percent"] <= 100 for r in topic_rows)
    return summary, topic_rows, advice_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()
    source = args.source_root.resolve()
    databases = [source/"app/threads/pokerstrategy_threads.db", source/"app/transcripts/insights.db"]
    protected = [source/"visualizations.ipynb"]
    for db in databases:
        protected.extend(Path(str(db)+s) for s in ("", "-wal", "-shm") if Path(str(db)+s).exists())
    before = {str(p.relative_to(source)): digest(p) for p in protected}
    with tempfile.TemporaryDirectory(prefix="poker-report-") as temp:
        temp = Path(temp)
        forum = read_snapshot(databases[0], temp/"forum.db")
        creator = read_snapshot(databases[1], temp/"creator.db")
        try:
            summary, topics, advice = analyze(forum, creator)
        finally:
            forum.close()
            creator.close()
    after = {str(p.relative_to(source)): digest(p) for p in protected}
    if before != after:
        raise RuntimeError("Source files changed during analysis; do not publish")
    out = ROOT/"data"
    out.mkdir(exist_ok=True)
    (out/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    write_csv(out/"topic-prevalence.csv", topics, list(topics[0]))
    write_csv(out/"advice-estimates.csv", advice, list(advice[0]))
    private = ROOT/"private"
    private.mkdir(exist_ok=True)
    (private/"analysis-verification.json").write_text(json.dumps({"source_sha256": before,
        "originals_unchanged": before == after, "checks": "integrity, foreign keys, topic uniqueness, denominators, bounds"}, indent=2)+"\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
