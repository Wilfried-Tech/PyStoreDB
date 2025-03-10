from __future__ import annotations

import abc
from typing import TypeVar, Generic, TYPE_CHECKING, Any, Callable

from . import FieldPath

_T = TypeVar('_T')
_U = TypeVar('_U')

if TYPE_CHECKING:
    from . import DocumentSnapshot, QueryDocumentSnapshot

__all__ = [
    'Query',
    'QuerySnapshot',
]


class Query(abc.ABC, Generic[_T]):
    """
    Represents an abstract base class for composing and executing queries on a dataset.

    The Query class provides an interface for defining, filtering, and manipulating
    queries that interact with a database or dataset. It supports various query operations
    such as filtering, ordering, limiting results, and aggregations. This is an abstract
    class that must be implemented by derived classes to provide specific functionality.

    Attributes:
        _T (Generic): Represents a generic parameter for the query result type.
    """

    @abc.abstractmethod
    def end_at_document(self, document: DocumentSnapshot) -> Query[_T]:
        """
        Ends the query at the specified document.

        Args:
            document (DocumentSnapshot): The document at which to end the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def end_at(self, *args) -> Query[_T]:
        """
        Ends the query at the specified position.

        Args:
            *args: The position at which to end the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def end_before_document(self, document: DocumentSnapshot) -> Query[_T]:
        """
        Ends the query before the specified document.

        Args:
            document (DocumentSnapshot): The document before which to end the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def end_before(self, *args) -> Query[_T]:
        """
        Ends the query before the specified position.

        Args:
            *args: The position before which to end the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def get(self) -> QuerySnapshot[_T]:
        """
        Executes the query and returns the results as a QuerySnapshot.

        Returns:
            QuerySnapshot[_T]: The query snapshot containing the results.
        """
        pass

    @abc.abstractmethod
    def limit(self, limit: int) -> Query[_T]:
        """
        Limits the number of results returned by the query.

        Args:
            limit (int): The maximum number of results to return.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def order_by(self, field: str | FieldPath, descending=False) -> Query[_T]:
        """
        Orders the results by the specified field.

        Args:
            field (str | FieldPath): The field by which to order the results.
            descending (bool, optional): Whether to order in descending order. Defaults to False.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def start_after_document(self, document: DocumentSnapshot) -> Query[_T]:
        """
        Starts the query after the specified document.

        Args:
            document (DocumentSnapshot): The document after which to start the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def start_after(self, *args) -> Query[_T]:
        """
        Starts the query after the specified position.

        Args:
            *args: The position after which to start the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def start_at_document(self, document: DocumentSnapshot) -> Query[_T]:
        """
        Starts the query at the specified document.

        Args:
            document (DocumentSnapshot): The document at which to start the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def start_at(self, *args) -> Query[_T]:
        """
        Starts the query at the specified position.

        Args:
            *args: The position at which to start the query.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def limit_to_last(self, limit: int) -> Query[_T]:
        """
        Limits the query to return only the last set of results.

        Args:
            limit (int): The maximum number of results to return.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def count(self) -> int:
        """
        Returns the count of documents that match the query.

        Returns:
            int: The count of matching documents.
        """
        pass

    @abc.abstractmethod
    def where(self, *args, **kwargs) -> Query[_T]:
        """
        Filters the query based on the specified conditions.

        Args:
            *args: Positional arguments for the filter conditions.
            **kwargs: Keyword arguments for the filter conditions.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def exclude(self, *args, **kwargs) -> Query[_T]:
        """
        Excludes documents from the query based on the specified conditions.

        Args:
            *args: Positional arguments for the exclusion conditions.
            **kwargs: Keyword arguments for the exclusion conditions.

        Returns:
            Query[_T]: The query instance.
        """
        pass

    @abc.abstractmethod
    def aggregate(self, *args) -> dict[str, Any]:
        """
        Aggregates the results of the query based on the specified aggregations.

        Args:
            *args: The aggregation operations to perform.

        Returns:
            dict[str, Any]: The aggregated results.
        """
        pass

    @abc.abstractmethod
    def with_converter(self, from_json: Callable[[_T], _U], to_json: Callable[[_U], _T]) -> Query[_U]:
        """
        Applies a converter to the query results.

        Args:
            from_json (Callable[[_T], _U]): A function to convert from JSON to the desired type.
            to_json (Callable[[_U], _T]): A function to convert from the desired type to JSON.

        Returns:
            Query[_U]: The query instance with the converter applied.
        """
        pass


class QuerySnapshot(abc.ABC, Generic[_T]):
    """Represents an abstract base class for a snapshot of a query.

    The QuerySnapshot provides a representation of the results of a query as a
    snapshot at a given point in time. This class is meant to be extended for
    specific implementations. It includes methods and properties to access the
    documents in the snapshot, the size of the snapshot, and a string representation
    of this snapshot.

    Attributes:
        docs (list[QueryDocumentSnapshot[_T]]): A list of documents snapshot
            contained in the query result.
        size (int): The number of documents contained in the query snapshot.
    """

    @property
    @abc.abstractmethod
    def docs(self) -> list[QueryDocumentSnapshot[_T]]:
        """
        Returns the list of document snapshots contained in the query result.

        Returns:
            list[QueryDocumentSnapshot[_T]]: The list of document snapshots.
        """
        pass

    @property
    @abc.abstractmethod
    def size(self) -> int:
        """
        Returns the number of documents contained in the query snapshot.

        Returns:
            int: The number of documents.
        """
        pass

    def __len__(self) -> int:
        """
        Returns the number of documents contained in the query snapshot.

        Returns:
            int: The number of documents.
        """
        return self.size

    def __repr__(self):
        """
        Returns a string representation of the query snapshot.

        Returns:
            str: The string representation of the query snapshot.
        """
        return f'<{self.__class__.__name__} {self.docs}>'
        pass
