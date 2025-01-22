from __future__ import annotations

import abc
from typing import Generic, TypeVar, Any

from PyStore.types import Json
from ._query import Query
from ..query import FieldPath

_T = TypeVar('_T')


# TODO: implement with converter

class StoreObject(abc.ABC):

    @property
    @abc.abstractmethod
    def path(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StoreObject):
            return False
        return self.path == other.path and self.id == other.id

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.path}')"


class CollectionReference(StoreObject, Query[_T], Generic[_T]):

    @abc.abstractmethod
    def add(self, data: _T) -> DocumentReference[_T]:
        pass

    @abc.abstractmethod
    def doc(self, key: str) -> DocumentReference[_T]:
        pass


class DocumentSnapshot(abc.ABC, Generic[_T]):

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
    def get(self, field: str | FieldPath) -> Any:
        pass

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __bool__(self):
        return self.exists


class DocumentReference(StoreObject, Generic[_T]):

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
    def update(self, data: Json, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def delete(self) -> None:
        pass
