import abc
from typing import Generic, TypeVar

from PyStore.core._common import DocumentSnapshot
from PyStore.core._json_document import JsonDocumentSnapshot
from PyStore.types import Json

_T = TypeVar('_T')


class QueryDocumentSnapshot(DocumentSnapshot[_T], Generic[_T]):

    @property
    @abc.abstractmethod
    def data(self) -> _T:
        pass


class JsonQueryDocumentSnapshot(JsonDocumentSnapshot):

    def __init__(self, delegate):
        super().__init__(delegate)

    @property
    def data(self) -> Json:
        return super().data

    @property
    def exists(self) -> bool:
        return True
