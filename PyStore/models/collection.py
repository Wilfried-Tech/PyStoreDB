from __future__ import annotations

from typing import TYPE_CHECKING

from PyStore.models import CollectionReference, DocumentReference
from PyStore.query import JsonQuery
from PyStore.types import Json
from .._delegates import CollectionDelegate

if TYPE_CHECKING:
    pass


class JsonCollectionReference(JsonQuery, CollectionReference[Json]):

    @property
    def path(self) -> str:
        return self._delegate.path

    @property
    def id(self) -> str:
        return self._delegate.id

    def doc(self, path: str | None = None) -> DocumentReference[Json]:
        from PyStore.models.document import JsonDocumentReference
        return JsonDocumentReference(self._delegate.doc(path))

    def add(self, data: Json) -> DocumentReference[Json]:
        doc = self.doc()
        doc.set(data)
        return doc

    def __init__(self, delegate: CollectionDelegate):
        super().__init__(delegate)
        self._delegate = delegate
