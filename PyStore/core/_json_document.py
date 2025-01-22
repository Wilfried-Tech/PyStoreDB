from __future__ import annotations

from typing import Any

from PyStore.core._common import DocumentSnapshot, DocumentReference, CollectionReference
from PyStore.types import Json
from ._delegates import DocumentDelegate
from ..query import FieldPath


class JsonDocumentReference(DocumentReference[Json]):
    @property
    def path(self) -> str:
        return self._delegate.path

    @property
    def id(self) -> str:
        return self._delegate.id

    @property
    def parent(self) -> CollectionReference[Json]:
        if self._delegate.parent is not None:
            from PyStore.core._json_collection import JsonCollectionReference
            return JsonCollectionReference(self._delegate.parent)

    def collection(self, path: str) -> CollectionReference[Json]:
        from PyStore.core._json_collection import JsonCollectionReference
        return JsonCollectionReference(self._delegate.collection(path))

    def update(self, data: Json = None, **kwargs) -> None:
        return self._delegate.update({**(data or {}), **kwargs})

    def get(self) -> DocumentSnapshot[Json]:
        return JsonDocumentSnapshot(self._delegate.get())

    def delete(self) -> None:
        self._delegate.delete()

    def set(self, data: Json, **kwargs) -> None:
        self._delegate.set({**data, **kwargs})

    def __init__(self, delegate: DocumentDelegate):
        self._delegate = delegate


class JsonDocumentSnapshot(DocumentSnapshot[Json]):

    @property
    def data(self) -> Json | None:
        return self._delegate.data()

    @property
    def reference(self) -> DocumentReference[Json]:
        return JsonDocumentReference(self._delegate.get())

    @property
    def id(self) -> str:
        return self._delegate.id

    def get(self, field: str|FieldPath) -> Any:
        return self._delegate.get_field(field)

    @property
    def exists(self) -> bool:
        return self._delegate.exists

    def __init__(self, delegate: DocumentDelegate):
        self._delegate = delegate
