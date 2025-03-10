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
        """Abstract property that represents the storage path of the object."""
        pass

    @property
    @abc.abstractmethod
    def id(self) -> str:
        """Abstract property that represents the unique identifier of the object."""
        pass

    def __eq__(self, other: Any) -> bool:
        """Check if two StoreObject instances are equal based on their path and id.

        Args:
            other (Any): The other object to compare with.

        Returns:
            bool: True if both objects have the same path and id, False otherwise.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.path == other.path and self.id == other.id

    def __repr__(self):
        """Return a string representation of the StoreObject instance.

        Returns:
            str: The string representation of the instance.
        """
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
        """Add a new document to the collection.

        Args:
            data (_T): The data to be added to the new document.

        Returns:
            DocumentReference[_T]: A reference to the newly added document.
        """
        pass

    @abc.abstractmethod
    def doc(self, path: str = None) -> DocumentReference[_T]:
        """Get a reference to a document in the collection.

        Args:
            path (str, optional): The path to the document. Defaults to None.

        Returns:
            DocumentReference[_T]: A reference to the document.
        """
        pass

    @abc.abstractmethod
    def with_converter(self, from_json: Callable[[_T], _U], to_json: Callable[[_U], _T]) -> CollectionReference[_U]:
        """Get a collection reference with data conversion functions.

        Args:
            from_json (Callable[[_T], _U]): Function to convert from JSON to the desired type.
            to_json (Callable[[_U], _T]): Function to convert from the desired type to JSON.

        Returns:
            CollectionReference[_U]: A collection reference with the specified data conversion functions.
        """
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
        """Get the unique identifier of the document.

        Returns:
            str: The unique identifier of the document.
        """
        pass

    @property
    @abc.abstractmethod
    def reference(self) -> DocumentReference[_T]:
        """Get the reference to the document in the database.

        Returns:
            DocumentReference[_T]: The reference to the document.
        """
        pass

    @property
    @abc.abstractmethod
    def exists(self) -> bool:
        """Check if the document exists in the database.

        Returns:
            bool: True if the document exists, False otherwise.
        """
        pass

    @property
    @abc.abstractmethod
    def data(self) -> _T | None:
        """Get the data of the document.

        Returns:
            _T | None: The data of the document, or None if the document does not exist.
        """
        pass

    @abc.abstractmethod
    def get(self, field: str | FieldPath, default=None) -> Any:
        """Get the value of a specific field in the document.

        Args:
            field (str | FieldPath): The field to retrieve the value from.
            default (Any, optional): The default value to return if the field does not exist. Defaults to None.

        Returns:
            Any: The value of the specified field.
        """
        pass

    def __getitem__(self, item: str) -> Any:
        """Get the value of a specific field using the indexing syntax.

        Args:
            item (str): The field to retrieve the value from.

        Returns:
            Any: The value of the specified field.
        """
        return self.get(item)

    def __bool__(self):
        """Check if the document exists using the boolean context.

        Returns:
            bool: True if the document exists, False otherwise.
        """
        return self.exists

    def __eq__(self, other: Any) -> bool:
        """Check if two DocumentSnapshot instances are equal based on their id and reference.

        Args:
            other (Any): The other object to compare with.

        Returns:
            bool: True if both objects have the same id and reference, False otherwise.
        """
        if not isinstance(other, DocumentSnapshot):
            return False
        return self.id == other.id and self.reference == other.reference

    def __repr__(self):
        """Return a string representation of the DocumentSnapshot instance.

        Returns:
            str: The string representation of the instance.
        """
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
        """Get the reference to the collection that contains this document.

        Returns:
            CollectionReference[_T]: The reference to the parent collection.
        """
        pass

    @abc.abstractmethod
    def collection(self, path: str) -> CollectionReference[_T]:
        """Get a reference to a sub-collection within this document.

        Args:
            path (str): The path to the sub-collection.

        Returns:
            CollectionReference[_T]: A reference to the sub-collection.
        """
        pass

    @abc.abstractmethod
    def set(self, data: _T, **kwargs) -> None:
        """Set the data of the document.

        Args:
            data (_T): The data to set in the document.
            **kwargs: Additional arguments for setting the data.
        """
        pass

    @abc.abstractmethod
    def get(self) -> DocumentSnapshot[_T]:
        """Get a snapshot of the document.

        Returns:
            DocumentSnapshot[_T]: A snapshot of the document.
        """
        pass

    @abc.abstractmethod
    def update(self, data: Json = None, **kwargs) -> None:
        """Update the data of the document.

        Args:
            data (Json, optional): The data to update in the document. Defaults to None.
            **kwargs: Additional arguments for updating the data.
        """
        pass

    @abc.abstractmethod
    def delete(self) -> None:
        """Delete the document."""
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
        """Get the core data contained in the document snapshot.

        Returns:
            _T: The core data contained in the document snapshot.
        """
        pass