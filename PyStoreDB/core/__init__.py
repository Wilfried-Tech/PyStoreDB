from __future__ import annotations

import abc
from typing import Generic, TypeVar, Any, Callable

from PyStoreDB.constants import Json
from PyStoreDB.core.filters import __all__ as _filters_all
from .field_path import FieldPath
from .query import Query, QuerySnapshot

_T = TypeVar('_T')
_U = TypeVar('_U')

__all__ = [
    'StoreObject',
    'CollectionReference',
    'DocumentSnapshot',
    'DocumentReference',
    'QueryDocumentSnapshot',
    'QuerySnapshot',
    'Query',
    'FieldPath',
    *_filters_all,
]


class StoreObject(abc.ABC):
    """
    Abstract base class for representing an object stored in a storage system.

    This class serves as a blueprint for objects that can be uniquely identified
    and accessed via a path in a storage system. Subclasses must implement the
    abstract methods to provide specific details about the object's path and
    identifier.

    Attributes:
        path (str): Abstract property that represents the storage path of the object.
        id (str): Abstract property that represents the unique identifier of the
            object.
    """

    @property
    @abc.abstractmethod
    def path(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.path == other.path and self.id == other.id

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.path}')"


class CollectionReference(StoreObject, Query[_T], Generic[_T]):
    """
    Represents a reference to a collection in a data store.

    This class serves as an abstraction for interacting with a collection in a
    data store. It provides methods for adding documents and retrieving a
    reference to a specific document by its key. The class should be subclassed,
    and the abstract methods should be implemented to provide the actual
    functionality for the specific type of data store.
    """

    @abc.abstractmethod
    def add(self, data: _T) -> DocumentReference[_T]:
        pass

    @abc.abstractmethod
    def doc(self, path: str = None) -> DocumentReference[_T]:
        pass

    @abc.abstractmethod
    def with_converter(self, from_json: Callable[[_T], _U], to_json: Callable[[_U], _T]) -> CollectionReference[_U]:
        pass


class DocumentSnapshot(abc.ABC, Generic[_T]):
    """
    Abstract base class representing a snapshot of a document.

    This class serves as a blueprint for creating document snapshot objects, which
    represent the state of a document in a database at a specific point in time. It
    provides a set of abstract methods and properties that must be implemented by
    subclasses to access document properties, retrieve data, and interact with the
    reference. Instances of this class allow querying and interacting with the
    document data in a structured way. It is a key component when working with
    documents in a database system like Firestore.

    Attributes:
        id (str): The unique identifier of the document.
        reference (DocumentReference[_T]): A reference to the document in the
            database.
        exists (bool): Indicates whether the document exists in the database.
        data (_T | None): The data of the document, or None if the document does
            not exist.
    """

    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def reference(self) -> DocumentReference[_T]:
        pass

    @property
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def data(self) -> _T | None:
        pass

    @abc.abstractmethod
    def get(self, field: str | FieldPath, default=None) -> Any:
        pass

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __bool__(self):
        return self.exists

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DocumentSnapshot):
            return False
        return self.id == other.id and self.reference == other.reference

    def __repr__(self):
        data = self.data
        if isinstance(data, dict):
            return f'<{self.__class__.__name__} {data}>'
        return str(data)


class DocumentReference(StoreObject, Generic[_T]):
    """
    Represents a reference to a document in a cloud or database system.

    This class serves as an abstract base class defining the structure
    and operations allowed on a document within a collection. It is intended
    for handling document operations such as reading, writing, updating, and
    deleting data. The data structure it operates on is generic and denoted
    by `_T`. Additionally, it provides methods to reference related
    collections or documents.

    Attributes:
        parent (CollectionReference[_T]): A reference to the collection that
            contains this document.
    """

    @property
    @abc.abstractmethod
    def parent(self) -> CollectionReference[_T]:
        pass

    @abc.abstractmethod
    def collection(self, path: str) -> CollectionReference[_T]:
        pass

    @abc.abstractmethod
    def set(self, data: _T, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def get(self) -> DocumentSnapshot[_T]:
        pass

    @abc.abstractmethod
    def update(self, data: Json = None, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def delete(self) -> None:
        pass


class QueryDocumentSnapshot(DocumentSnapshot[_T], Generic[_T]):
    """Represents a query document snapshot.

    This class provides an abstraction for a snapshot of a document as queried
    from a database. It inherits from `DocumentSnapshot` and applies a generic
    type `_T`, allowing flexibility in the data structure and type management
    for documents retrieved during database operations.

    Attributes:
        data (_T): Abstract property that defines the core data contained in the
            document snapshot. The type `_T` is user-defined and determined by
            the generic provided.
    """

    @property
    @abc.abstractmethod
    def data(self) -> _T:
        pass
