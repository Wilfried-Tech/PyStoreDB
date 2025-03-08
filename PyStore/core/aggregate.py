import abc
import statistics

from PyStore.core import FieldPath, QueryDocumentSnapshot


class Aggregation(abc.ABC):
    """
    Represents an abstract base class for data aggregation.

    This class serves as a blueprint for implementing specific aggregation
    strategies. It requires a field name to operate upon, which can either
    be a `FieldPath` object or a string representing the field name. Subclasses
    must provide an implementation for the `apply` method, which defines how
    the aggregation is performed on a given set of documents.

    :ivar field_name: The field name on which the aggregation operates.
    :type field_name: FieldPath
    """

    def __init__(self, field_name: FieldPath | str):
        self.field_name = field_name if isinstance(field_name, FieldPath) else FieldPath(field_name)

    @abc.abstractmethod
    def apply(self, docs):
        pass

    def get_numeric_values(self, docs: list[QueryDocumentSnapshot]) -> list[int | float]:
        return [doc.get(self.field_name) for doc in docs if isinstance(doc.get(self.field_name), (int, float))]


class Count(Aggregation):
    """
    Represents a counting aggregation operation.

    This class allows for counting the number of documents in a collection
    based on certain field criteria. It optionally supports counting distinct
    values for the specified field, providing flexible aggregation capabilities.

    :ivar field_name: The name of the field to count in the documents.
    :type field_name: FieldPath | str | None
    :ivar distinct: Whether to count only distinct values of the field.
    :type distinct: bool
    """

    def __init__(self, field_name: FieldPath | str = None, distinct: bool = False):
        super().__init__(field_name)
        self.distinct = distinct

    def apply(self, docs: list[QueryDocumentSnapshot]):
        cls = set if self.distinct else list
        return len(cls(doc.get(self.field_name) for doc in docs if doc.get(self.field_name) is not None))


class Sum(Aggregation):
    """
    The Sum class is a specific type of Aggregation that calculates the total sum
    of values for a specified field across a collection of documents.

    This class is used primarily for numerical aggregation tasks where the user
    needs to sum up all the numeric values present in a specific field of a
    collection of documents. It ensures that only numeric values are considered
    in the summation process by filtering out non-numeric values beforehand.

    :ivar field_name: The name of the field in the document whose values are
                      to be summed.
    :type field_name: str
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        return sum(self.get_numeric_values(docs))


class Min(Aggregation):
    """
    Represents an aggregation operation that calculates the minimum value
    of a specified numeric field.
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        return min(self.get_numeric_values(docs), default=None)


class Max(Aggregation):
    """
    Represents an aggregation operation that calculates the maximum value
    of a specified numeric field.
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        return max(self.get_numeric_values(docs), default=None)


class Mode(Aggregation):
    """
    Represents an aggregation operation that calculates the mode
    (most frequent value) of a specified numeric field.
    Notes
        if all values are unique, the first value is returned
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        values = self.get_numeric_values(docs)
        if len(values) == 0:
            return None
        return statistics.mode(self.get_numeric_values(docs))


class Variance(Aggregation):
    """
    Represents an aggregation operation to calculate the variance
    of numeric values for a certain field.
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        valid_values = self.get_numeric_values(docs)
        n = len(valid_values)
        if n < 2:
            return None
        return statistics.variance(valid_values)


class Median(Aggregation):
    """
    Represents an aggregation operation to calculate the median
    of numeric values for a certain field.
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        valid_values = sorted(self.get_numeric_values(docs))
        n = len(valid_values)
        if n == 0:
            return None
        return statistics.median(valid_values)


class StdDev(Aggregation):
    """
    Represents an aggregation operation to calculate the standard deviation
    of numeric values for a certain field.
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        valid_values = self.get_numeric_values(docs)
        n = len(valid_values)
        if n < 2:
            return None
        return statistics.stdev(valid_values)


class Avg(Aggregation):
    """
    Represents an aggregation operation to calculate the average
    (mean) value of numeric values for a certain field.
    """

    def apply(self, docs: list[QueryDocumentSnapshot]):
        valid_values = self.get_numeric_values(docs)
        return statistics.mean(valid_values) if valid_values else None
