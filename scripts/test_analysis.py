"""Synthetic checks of counting rules; never opens the original databases."""
import unittest
from analyze_saved_data import merge_identical_hands, unique_topics, summarize_topics, collapse_exact_rows


class CountingRules(unittest.TestCase):
    def test_identical_hand_merge_keeps_children_from_both_ids(self):
        hands, mapping = merge_identical_hands([
            {"id": 2, "thread_id": 10, "outcome": "unknown"},
            {"id": 1, "thread_id": 10, "outcome": "unknown"}])
        pairs = unique_topics([(1, "a"), (2, "b")], {"a": "topic-a", "b": "topic-b"}, mapping)
        self.assertEqual(len(hands), 1)
        self.assertEqual(pairs, {(1, "topic-a"), (1, "topic-b")})

    def test_separate_threads_are_not_merged(self):
        hands, mapping = merge_identical_hands([
            {"id": 1, "thread_id": 10, "outcome": "unknown"},
            {"id": 2, "thread_id": 11, "outcome": "unknown"}])
        self.assertEqual(len(hands), 2)

    def test_repeated_aliases_count_once_but_distinct_records_count_twice(self):
        pairs = unique_topics([(1, "a"), (1, "a2"), (1, "a"), (2, "a")], {"a": "topic", "a2": "topic"})
        denominator, counts = summarize_topics(pairs)
        self.assertEqual((denominator, counts["topic"]), (2, 2))

    def test_multilabel_denominator_is_entities_not_tags(self):
        denominator, counts = summarize_topics({(1, "a"), (1, "b"), (2, "a")})
        self.assertEqual(denominator, 2)
        self.assertEqual(sum(counts.values()), 3)

    def test_unmapped_label_fails_instead_of_disappearing(self):
        with self.assertRaises(ValueError):
            unique_topics([(1, "missing")], {})

    def test_reply_audit_does_not_merge_different_hands_or_sentiment(self):
        rows = [{"id": i, "hand_id": h, "text": "synthetic", "sentiment": s}
                for i, h, s in [(1, 1, 0), (2, 1, 0), (3, 2, 0), (4, 1, 1)]]
        self.assertEqual(len(collapse_exact_rows(rows)), 3)


if __name__ == "__main__":
    unittest.main()
