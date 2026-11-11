"""Draw explanatory SVGs from the reviewed project architecture (standard library).

These are diagrams of the saved workflow, not new extraction results. The hand
example is invented. Wide and narrow layouts keep labels legible on phones.
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "figures"
INK, MUTED, LINE, BRASS, SLATE = "#302923", "#6e6255", "#d3c6b3", "#86643b", "#526674"


class Diagram:
    def __init__(self, width, height, title, description):
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{BRASS}"/></marker></defs>
<style>text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;fill:{INK}}}.kicker{{font-size:12px;letter-spacing:1.5px;font-weight:700;fill:{BRASS}}}.heading{{font-family:Georgia,serif;font-size:23px}}.body{{font-size:16px}}.small{{font-size:14px;fill:{MUTED}}}.key{{font-size:13px;fill:{SLATE};font-family:ui-monospace,Consolas,monospace}}</style>''']

    def text(self, x, y, text, style="body", anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" class="{style}" text-anchor="{anchor}">{escape(text)}</text>')

    def box(self, x, y, w, h, title, lines=(), key=None, highlight=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{"#eee5d8" if highlight else "#faf6ee"}" stroke="{BRASS if highlight else LINE}"/>')
        self.text(x+18, y+32, title, "heading")
        for i, line in enumerate(lines):
            self.text(x+18, y+58+23*i, line)
        if key:
            self.text(x+18, y+h-16, key, "key")

    def arrow(self, points, label=None, lx=None, ly=None):
        self.parts.append(f'<path d="{points}" fill="none" stroke="{BRASS}" stroke-width="1.8" marker-end="url(#arrow)"/>')
        if label:
            # A paper backing breaks the connector behind its annotation.
            width = len(label) * 7.4 + 14
            self.parts.append(f'<rect x="{lx-width/2}" y="{ly-15}" width="{width}" height="20" fill="#f7f2e8"/>')
            self.text(lx, ly, label, "small", "middle")

    def save(self, name):
        OUT.mkdir(exist_ok=True)
        (OUT / f"{name}.svg").write_text("\n".join(self.parts)+"\n</svg>\n")


def pipeline(narrow=False):
    d = Diagram(360 if narrow else 880, 1100 if narrow else 655,
                "Two sources, one analytical workflow",
                "Forum discussions and video transcripts are prepared, extracted with language models, and saved in separate SQLite databases. A shared topic dictionary connects their labels. The 2026 reading edition compares distinct records using the saved data.")
    if narrow:
        d.text(18, 23, "FORUM DISCUSSIONS", "kicker")
        d.box(18, 40, 324, 112, "1,003 threads", ["Parse posts, replies and card suits.", "Keep the source and context."])
        d.arrow("M 180 152 V 202", "o4-mini extracts structured fields", 180, 181)
        d.box(18, 207, 324, 112, "Forum database", ["1,037 stored hand records", "Players, actions, replies and tags"])
        d.text(18, 365, "VIDEO TRANSCRIPTS", "kicker")
        d.box(18, 382, 324, 135, "75 videos", ["Retrieve transcript segments.", "GPT-4.1 prepares the text.", "Keep raw and prepared copies."])
        d.arrow("M 180 517 V 567", "o4-mini assigns video descriptors", 180, 546)
        d.box(18, 572, 324, 112, "Video database", ["69 saved label records", "Topics, type and advice estimate"])
        d.arrow("M 18 263 H 7 V 750 H 17")
        d.arrow("M 180 684 V 716")
        d.box(18, 721, 324, 135, "A shared topic dictionary", ["284 wording variants", "map to 262 common labels.", "Both sources use this mapping."], highlight=True)
        d.arrow("M 180 856 V 919", "2026 reading edition · saved data only", 180, 892)
        d.box(18, 924, 324, 145, "Compare the patterns", ["Count each record once per topic.", "Use a separate total per source.", "Visualize topic shares and", "video advice estimates."], highlight=True)
    else:
        d.text(20, 25, "FORUM DISCUSSIONS", "kicker")
        d.text(460, 25, "VIDEO TRANSCRIPTS", "kicker")
        d.box(20, 43, 400, 120, "1,003 threads", ["Parse posts, replies and card suits.", "Keep the source and context."])
        d.box(460, 43, 400, 120, "75 videos", ["Retrieve segments; prepare with GPT-4.1.", "Keep raw and prepared transcripts."])
        d.arrow("M 220 163 V 218", "o4-mini extracts structured fields", 220, 194)
        d.arrow("M 660 163 V 218", "o4-mini assigns video descriptors", 660, 194)
        d.box(20, 223, 400, 112, "Forum database", ["1,037 stored hand records", "Players, actions, replies and topic tags"])
        d.box(460, 223, 400, 112, "Video database", ["69 saved label records", "Topics, content type and advice estimate"])
        d.arrow("M 220 335 V 365 H 380 V 390")
        d.arrow("M 660 335 V 365 H 500 V 390")
        d.box(180, 395, 520, 94, "A shared topic dictionary", ["284 wording variants → 262 common labels"], highlight=True)
        d.arrow("M 440 489 V 544", "2026 reading edition · saved data only", 440, 521)
        d.box(180, 549, 520, 91, "Compare the patterns", ["Distinct records → topic shares and advice estimates"], highlight=True)
    d.save("project-pipeline"+("-mobile" if narrow else ""))


def extraction(narrow=False):
    d = Diagram(360 if narrow else 880, 855 if narrow else 560,
                "How a hand story becomes linked records",
                "An invented story becomes one hand record with related players, betting-round actions and topic tags. Each child record carries the hand ID. The same hand can have multiple tags without being counted as multiple hands.")
    if narrow:
        d.text(18, 23, "INVENTED HAND STORY", "kicker")
        d.box(18, 40, 324, 165, "A player describes a decision", ["“I raised with ace–ten. One player", "called. After the first three shared", "cards, I bet again. They folded.”", "The story supplies context and actions."])
        d.arrow("M 180 205 V 256", "Extract fields and attach a record ID", 180, 235)
        d.box(18, 261, 324, 94, "One hand record", ["Player cards: ace–ten"], key="id: example-1", highlight=True)
        for y, title, lines in [(415,"Two participants",["The player and one opponent"]), (550,"One betting round",["Player bets; opponent folds"]), (685,"Two topic tags",["One preflop raise", "Continuation bet on the flop"])]:
            d.arrow(f"M 29 355 V {y+45} H 45")
            d.box(50, y, 292, 115, title, lines, key="hand_id: example-1")
        d.text(18, 836, "The linking ID keeps the story together.", "small")
    else:
        d.text(20, 25, "INVENTED HAND STORY", "kicker")
        d.box(20, 43, 840, 100, "A player describes a decision", ["“I raised with ace–ten. One player called. After the first three shared cards,", "I bet again. They folded.”"])
        d.arrow("M 440 143 V 200", "Extract fields and attach a record ID", 440, 177)
        d.box(240, 205, 400, 106, "One hand record", ["Player cards: ace–ten"], key="id: example-1", highlight=True)
        d.arrow("M 440 311 V 350 H 153 V 390")
        d.arrow("M 440 311 V 390")
        d.arrow("M 440 311 V 350 H 727 V 390")
        d.box(20, 395, 266, 124, "Two participants", ["The player and", "one opponent"], key="hand_id: example-1")
        d.box(307, 395, 266, 124, "One betting round", ["Player bets;", "opponent folds"], key="hand_id: example-1")
        d.box(594, 395, 266, 124, "Two topic tags", ["One preflop raise", "Continuation bet on flop"], key="hand_id: example-1")
        d.text(440, 550, "The linking ID keeps the story together; two tags still describe one hand.", "small", "middle")
    d.save("story-to-records"+("-mobile" if narrow else ""))


def architecture(narrow=False):
    d = Diagram(360 if narrow else 880, 1205 if narrow else 850,
                "The database relationships behind the analysis",
                "One forum thread can have many hands. Each hand can have players, replies, street metrics and archetypes. One video has zero or one video_labels row. The analytical topic join uses the archetype_bridge alias mapping; dashed links are analytical joins, not foreign keys.")
    if narrow:
        d.text(18, 23, "FORUM DATABASE", "kicker")
        d.box(18, 40, 324, 94, "Discussions · threads", ["Post, source URL and reply text"], key="id")
        d.arrow("M 180 134 V 183", "one discussion → many hand records", 180, 163)
        d.box(18, 188, 324, 94, "Hand accounts · hands", ["Cards, position and context"], key="id · thread_id → threads.id", highlight=True)
        d.arrow("M 180 282 V 331", "one hand → several related records", 180, 311)
        d.box(18, 336, 324, 183, "Related tables", ["players · participants", "replies · comments and tone", "street_metrics · actions by round", "archetypes · strategy topic tags"], key="each uses hand_id → hands.id")
        d.text(18, 568, "VIDEO DATABASE", "kicker")
        d.box(18, 585, 324, 94, "Collected videos · videos", ["Title, URL and transcript"], key="video_id")
        d.arrow("M 180 679 V 728", "one video → zero or one label record", 180, 708)
        d.box(18, 733, 324, 94, "Descriptors · video_labels", ["Type, topic list and advice estimate"], key="video_id → videos.video_id")
        d.arrow("M 18 469 H 7 V 930 H 17")
        d.arrow("M 180 827 V 890", "expand the video topic list", 180, 863)
        d.box(18, 895, 324, 117, "Shared topic mapping", ["archetype_bridge", "Wording variant → common label"], key="an analytical join, not a foreign key", highlight=True)
        d.arrow("M 180 1012 V 1061")
        d.box(18, 1066, 324, 117, "Comparable topic counts", ["One hand–topic pair counts once.", "One video–topic pair counts once."], highlight=True)
    else:
        d.text(20, 25, "FORUM DATABASE", "kicker")
        d.text(500, 25, "VIDEO DATABASE", "kicker")
        d.box(20, 43, 420, 98, "Discussions · threads", ["Post, source URL and reply text"], key="id")
        d.box(500, 43, 360, 98, "Collected videos · videos", ["Title, URL and transcript"], key="video_id")
        d.arrow("M 230 141 V 201", "one discussion → many hand records", 230, 176)
        d.arrow("M 680 141 V 201", "one video → zero or one label record", 680, 176)
        d.box(20, 206, 420, 98, "Hand accounts · hands", ["Cards, position and context"], key="id · thread_id → threads.id", highlight=True)
        d.box(500, 206, 360, 98, "Descriptors · video_labels", ["Type, topics and advice estimate"], key="video_id → videos.video_id")
        d.arrow("M 230 304 V 363", "one hand → several related records", 230, 338)
        d.box(20, 368, 420, 185, "Related tables", ["players · participants", "replies · comments and tone", "street_metrics · actions by betting round", "archetypes · strategy topic tags"], key="each uses hand_id → hands.id")
        d.arrow("M 680 304 V 363", "expand the topic list", 680, 338)
        d.box(500, 368, 360, 98, "Video–topic pairs", ["One derived row per video and tag"], key="analysis step; not a stored table")
        # These connectors deliberately differ from primary/foreign-key links.
        d.parts.append(f'<path d="M 440 493 H 470 V 600 H 385 V 627 M 680 466 V 600 H 515 V 627" fill="none" stroke="{SLATE}" stroke-width="1.8" stroke-dasharray="5 5"/>')
        d.box(180, 632, 520, 98, "Shared topic mapping · archetype_bridge", ["Wording variants → common topic labels"], key="dashed lines: analytical joins, not foreign keys", highlight=True)
        d.arrow("M 440 730 V 765")
        d.box(180, 770, 520, 68, "Count each hand–topic or video–topic pair once", highlight=True)
    d.save("database-architecture"+("-mobile" if narrow else ""))


if __name__ == "__main__":
    for narrow in (False, True):
        pipeline(narrow)
        extraction(narrow)
        architecture(narrow)
    print("Created three explanatory diagrams, each with wide and mobile layouts.")
