import unittest
from unittest.mock import MagicMock

from PyStoreDB.core import FieldPath, QueryDocumentSnapshot
from PyStoreDB.core.aggregate import Count, Sum, Min, Max, Mode, Variance, Median, StdDev, Avg


class TestAggregation(unittest.TestCase):
    def setUp(self):
        self.docs = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 2}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 4}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': None}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 4}),
        ]
        self.empty_docs = []
        self.field = FieldPath("test_field")

    def test_count(self):
        count_aggregation = Count(self.field)
        result = count_aggregation.apply(self.docs)
        self.assertEqual(result, 3)

        distinct_count_aggregation = Count(self.field, distinct=True)
        result = distinct_count_aggregation.apply(self.docs)
        self.assertEqual(result, 2)

        result = count_aggregation.apply(self.empty_docs)
        self.assertEqual(result, 0)

    def test_sum(self):
        sum_aggregation = Sum(self.field)
        result = sum_aggregation.apply(self.docs)
        self.assertEqual(result, 10)

        result = sum_aggregation.apply(self.empty_docs)
        self.assertEqual(result, 0)

        docs_with_negative = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': -3}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
        ]
        result = sum_aggregation.apply(docs_with_negative)
        self.assertEqual(result, 2)

    def test_min(self):
        min_aggregation = Min(self.field)
        result = min_aggregation.apply(self.docs)
        self.assertEqual(result, 2)

        result = min_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_negatives = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': -3}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': -10}),
        ]
        result = min_aggregation.apply(docs_with_negatives)
        self.assertEqual(result, -10)

    def test_max(self):
        max_aggregation = Max(self.field)
        result = max_aggregation.apply(self.docs)
        self.assertEqual(result, 4)

        result = max_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_negatives = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 3}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': -1}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 10}),
        ]
        result = max_aggregation.apply(docs_with_negatives)
        self.assertEqual(result, 10)

    def test_mode(self):
        mode_aggregation = Mode(self.field)
        result = mode_aggregation.apply(self.docs)
        self.assertEqual(result, 4)

        result = mode_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_unique_values = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 1}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 2}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 3}),
        ]
        result = mode_aggregation.apply(docs_with_unique_values)
        self.assertEqual(result, 1, "Mode should return the first value if all values are unique")

    def test_variance(self):
        variance_aggregation = Variance(self.field)
        result = variance_aggregation.apply(self.docs)
        self.assertAlmostEqual(result, 1.3333, places=4)

        result = variance_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_same_values = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
        ]
        result = variance_aggregation.apply(docs_with_same_values)
        self.assertEqual(result, 0)

    def test_median(self):
        median_aggregation = Median(self.field)
        result = median_aggregation.apply(self.docs)
        self.assertEqual(result, 4)

        result = median_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_odd_values = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 1}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 3}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
        ]
        result = median_aggregation.apply(docs_with_odd_values)
        self.assertEqual(result, 3)

    def test_stddev(self):
        stddev_aggregation = StdDev(self.field)
        result = stddev_aggregation.apply(self.docs)
        self.assertAlmostEqual(result, 1.1547, places=4)

        result = stddev_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_same_values = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
        ]
        result = stddev_aggregation.apply(docs_with_same_values)
        self.assertEqual(result, 0)

    def test_avg(self):
        avg_aggregation = Avg(self.field)
        result = avg_aggregation.apply(self.docs)
        self.assertEqual(result, 10 / 3)

        result = avg_aggregation.apply(self.empty_docs)
        self.assertIsNone(result)

        docs_with_single_value = [
            MagicMock(spec=QueryDocumentSnapshot, **{'get.return_value': 5}),
        ]
        result = avg_aggregation.apply(docs_with_single_value)
        self.assertEqual(result, 5)


if __name__ == '__main__':
    unittest.main()
