from __future__ import annotations

import abc
from typing import TypeVar, Generic, TYPE_CHECKING

from . import FieldPath
from .snapshot import QuerySnapshot

_T = TypeVar('_T')

if TYPE_CHECKING:
    from PyStore.models import DocumentSnapshot


class Query(abc.ABC, Generic[_T]):

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
    def where(self, **kwargs) -> Query[_T]:
        pass

    @abc.abstractmethod
    def aggregate(self, *args) -> Query[_T]:
        pass
