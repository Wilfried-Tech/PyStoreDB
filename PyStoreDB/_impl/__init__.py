from __future__ import annotations

from functools import cached_property
from typing import Any, TypeVar

from PyStoreDB._delegates import DocumentDelegate, CollectionDelegate, QueryDelegate
from PyStoreDB._impl.converter import FromPyStoreDB, ToPyStoreDB
from PyStoreDB._impl.query import JsonQuery
from PyStoreDB.constants import Json
from PyStoreDB.core import (
    DocumentReference,
    DocumentSnapshot,
    CollectionReference,
    FieldPath,
    QueryDocumentSnapshot,
    QuerySnapshot
)

__all__ = [
    'JsonDocumentReference',
    'JsonDocumentSnapshot',
    'JsonCollectionReference',
    'JsonQuery',
    'JsonQuerySnapshot',
    'JsonQueryDocumentSnapshot',
]

_T = TypeVar('_T')

from PyStoreDB.core.aggregate import Count


class JsonDocumentReference(DocumentReference[Json]):
    @property
    def path(self) -> str:
        return self._delegate.path

    @property
    def id(self) -> str:
        return self._delegate.id

    @property
    def parent(self) -> CollectionReference[Json]:
        return JsonCollectionReference(self._delegate.parent)

    def collection(self, path: str) -> CollectionReference[Json]:
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

    def get(self, field: str | FieldPath, default=None) -> Any:
        return self._delegate.get_field(field, default)

    @property
    def exists(self) -> bool:
        return self._delegate.exists

    def __init__(self, delegate: DocumentDelegate):
        self._delegate = delegate


class JsonQueryDocumentSnapshot(JsonDocumentSnapshot, QueryDocumentSnapshot[Json]):

    def __init__(self, delegate):
        super().__init__(delegate)

    @property
    def data(self) -> Json:
        return super().data

    @property
    def exists(self) -> bool:
        return True


class JsonQuerySnapshot(QuerySnapshot[Json]):

    def __init__(self, delegate: QueryDelegate):
        self._delegate = delegate

    @cached_property
    def docs(self) -> list[JsonQueryDocumentSnapshot]:
        data = self._delegate.engine.get_collection(self._delegate.path, **self._delegate.kwargs)
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
        return Count(FieldPath.document_id).apply(self.docs)


class JsonCollectionReference(JsonQuery, CollectionReference[Json]):

    def with_converter(self, from_json: FromPyStoreDB[_T], to_json: ToPyStoreDB[_T]) -> CollectionReference[_T]:
        from PyStoreDB._impl.converter import WithConverterCollectionReference
        return WithConverterCollectionReference[_T](self, from_json, to_json)

    @property
    def path(self) -> str:
        return self._delegate.path

    @property
    def id(self) -> str:
        return self._delegate.id

    def doc(self, path: str | None = None) -> DocumentReference[Json]:
        return JsonDocumentReference(self._delegate.doc(path))

    def add(self, data: Json) -> DocumentReference[Json]:
        doc = self.doc()
        doc.set(data)
        return doc

    def __init__(self, delegate: CollectionDelegate):
        super().__init__(delegate)
        self._delegate = delegate


if __name__ != 'PyStoreDB._impl':
    raise ImportError('This module cannot be imported directly')
