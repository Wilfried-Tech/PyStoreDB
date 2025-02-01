from __future__ import annotations

import abc
from functools import cached_property
from typing import TypeVar, Generic, TYPE_CHECKING

from .._delegates import QueryDelegate
from PyStore.types import Json
from .._delegates import DocumentDelegate

_T = TypeVar('_T')

if TYPE_CHECKING:
    from .document_snapshot import JsonQueryDocumentSnapshot


class QuerySnapshot(abc.ABC, Generic[_T]):

    @property
    @abc.abstractmethod
    def docs(self) -> list[JsonQueryDocumentSnapshot]:
        pass

    @property
    @abc.abstractmethod
    def size(self) -> int:
        pass


class JsonQuerySnapshot(QuerySnapshot[Json]):

    def __init__(self, delegate: QueryDelegate):
        self._delegate = delegate

    @cached_property
    def docs(self) -> list[JsonQueryDocumentSnapshot]:
        data = self._delegate.engine.get_collection(self._delegate.path, **self._delegate.kwargs)
        from .document_snapshot import JsonQueryDocumentSnapshot
        return [
            JsonQueryDocumentSnapshot(
                DocumentDelegate(
                    f'{self._delegate.path}/{_id}',
                    self._delegate.engine,
                )
            )
            for _id, doc in data.items()
        ]

    @property
    def size(self) -> int:
        return len(list(self.docs))
