from __future__ import annotations

import abc
from typing import TypeVar, Generic, TYPE_CHECKING, Generator, Any

from PyStore.core._query.delegate import QueryDelegate
from PyStore.types import Json
from .._delegates import DocumentDelegate

_T = TypeVar('_T')

if TYPE_CHECKING:
    from .._query.query_document_snapshot import JsonQueryDocumentSnapshot


class QuerySnapshot(abc.ABC, Generic[_T]):

    @property
    @abc.abstractmethod
    def docs(self) -> Generator[JsonQueryDocumentSnapshot, Any, None]:
        pass

    @property
    @abc.abstractmethod
    def size(self) -> int:
        pass


class JsonQuerySnapshot(QuerySnapshot[Json]):

    def __init__(self, delegate: QueryDelegate):
        self._delegate = delegate

    @property
    def docs(self) -> Generator[JsonQueryDocumentSnapshot, Any, None]:
        data = self._delegate.engine.get_collection(self._delegate.path, **self._delegate.parameters)

        from .._query.query_document_snapshot import JsonQueryDocumentSnapshot

        for _id, doc in data.items():
            yield JsonQueryDocumentSnapshot(
                DocumentDelegate(
                    f'{self._delegate.path}/{_id}',
                    self._delegate.engine,
                )
            )

    @property
    def size(self) -> int:
        return len(list(self.docs))
