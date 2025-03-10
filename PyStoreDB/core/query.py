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
        pass

    @abc.abstractmethod
    def end_at(self, *args) -> Query[_T]:
        pass

    @abc.abstractmethod
    def end_before_document(self, document: DocumentSnapshot) -> Query[_T]:
        pass

    @abc.abstractmethod
    def end_before(self, *args) -> Query[_T]:
        pass

    @abc.abstractmethod
    def get(self) -> QuerySnapshot[_T]:
        pass

    @abc.abstractmethod
    def limit(self, limit: int) -> Query[_T]:
        pass

    @abc.abstractmethod
    def order_by(self, field: str | FieldPath, descending=False) -> Query[_T]:
        pass

    @abc.abstractmethod
    def start_after_document(self, document: DocumentSnapshot) -> Query[_T]:
        pass

    @abc.abstractmethod
    def start_after(self, *args) -> Query[_T]:
        pass

    @abc.abstractmethod
    def start_at_document(self, document: DocumentSnapshot) -> Query[_T]:
        pass

    @abc.abstractmethod
    def start_at(self, *args) -> Query[_T]:
        pass

    @abc.abstractmethod
    def limit_to_last(self, limit: int) -> Query[_T]:
        pass

    @abc.abstractmethod
    def count(self) -> int:
        pass

    @abc.abstractmethod
    def where(self, *args, **kwargs) -> Query[_T]:
        pass

    @abc.abstractmethod
    def exclude(self, *args, **kwargs) -> Query[_T]:
        pass

    @abc.abstractmethod
    def aggregate(self, *args) -> dict[str, Any]:
        pass

    @abc.abstractmethod
    def with_converter(self, from_json: Callable[[_T], _U], to_json: Callable[[_U], _T]) -> Query[_U]:
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
        pass

    @property
    @abc.abstractmethod
    def size(self) -> int:
        pass

    def __len__(self) -> int:
        return self.size

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.docs}>'
