from typing import TypeVar, Any, Callable, Generic, cast

from PyStoreDB.constants import Json
from PyStoreDB.core import (
    DocumentReference,
    CollectionReference,
    QuerySnapshot,
    DocumentSnapshot,
    QueryDocumentSnapshot,
    Query,
    FieldPath
)

_T = TypeVar('_T')
_U = TypeVar('_U')
FromPyStoreDB = Callable[[DocumentSnapshot], _T]
ToPyStoreDB = Callable[[_T], Json]


class WithConverterDocumentReference(DocumentReference[_T], Generic[_T]):

    @property
    def id(self) -> str:
        return self._original_reference.id

    @property
    def path(self) -> str:
        return self._original_reference.path

    def delete(self) -> None:
        return self._original_reference.delete()

    def update(self, data: _T = None, **kwargs) -> None:
        if data is not None:
            return self._original_reference.update(self._to_json(data), **kwargs)
        return self._original_reference.update(**kwargs)

    def set(self, data: _T, **kwargs) -> None:
        return self._original_reference.set(self._to_json(data), **kwargs)

    @property
    def parent(self) -> CollectionReference[_T]:
        return WithConverterCollectionReference(self._original_reference.parent, self._from_json, self._to_json)

    def collection(self, path: str) -> CollectionReference[_T]:
        return WithConverterCollectionReference(
            self._original_reference.collection(path),
            self._from_json,
            self._to_json
        )

    def get(self) -> DocumentSnapshot[_T]:
        return WithConverterDocumentSnapshot(self._original_reference.get(), self._from_json, self._to_json)

    def __init__(
            self,
            original_reference: DocumentReference[Json],
            from_json: FromPyStoreDB[_T],
            to_json: ToPyStoreDB[_T]
    ):
        self._original_reference = original_reference
        self._from_json = from_json
        self._to_json = to_json


class WithConverterDocumentSnapshot(DocumentSnapshot[_T], Generic[_T]):

    @property
    def id(self) -> str:
        return self._original_snapshot.id

    @property
    def reference(self) -> DocumentReference[_T]:
        return WithConverterDocumentReference(self._original_snapshot.reference, self._from_json, self._to_json)

    @property
    def exists(self) -> bool:
        return self._original_snapshot.exists

    @property
    def data(self) -> _T | None:
        if self._original_snapshot.exists:
            return self._from_json(self._original_snapshot)
        return None

    def get(self, field: str | FieldPath, default=None) -> Any:
        return self._original_snapshot.get(field, default)

    def __init__(
            self,
            original_snapshot: DocumentSnapshot[Json],
            from_json: FromPyStoreDB[_T],
            to_json: ToPyStoreDB[_T]
    ):
        self._original_snapshot = original_snapshot
        self._from_json = from_json
        self._to_json = to_json


class WithConverterQueryDocumentSnapshot(WithConverterDocumentSnapshot[_T], QueryDocumentSnapshot[_T], Generic[_T]):

    def __init__(
            self,
            original_snapshot: DocumentSnapshot[Json],
            from_json: FromPyStoreDB[_T],
            to_json: ToPyStoreDB[_T]
    ):
        super().__init__(original_snapshot, from_json, to_json)

    @property
    def data(self) -> _T:
        return self._from_json(self._original_snapshot)

    @property
    def exists(self) -> bool:
        return True


class WithConverterQuerySnapshot(QuerySnapshot[_T], Generic[_T]):

    @property
    def docs(self) -> list[QueryDocumentSnapshot[_T]]:
        return [
            WithConverterQueryDocumentSnapshot(doc, self._from_json, self._to_json)
            for doc in self._original_snapshot.docs
        ]

    @property
    def size(self) -> int:
        return self._original_snapshot.size

    def __init__(
            self,
            original_snapshot: QuerySnapshot[Json],
            from_json: FromPyStoreDB[_T],
            to_json: ToPyStoreDB[_T]
    ):
        self._original_snapshot = original_snapshot
        self._from_json = from_json
        self._to_json = to_json


class WithConverterQuery(Query[_T], Generic[_T]):

    def _map_query(self, new_query: Query[Json]) -> Query[_T]:
        return WithConverterQuery(new_query, self._from_json, self._to_json)

    def end_at_document(self, document: DocumentSnapshot) -> Query[_T]:
        return self._map_query(self._original_query.end_at_document(document))

    def end_at(self, *args) -> Query[_T]:
        return self._map_query(self._original_query.end_at(*args))

    def end_before_document(self, document: DocumentSnapshot) -> Query[_T]:
        return self._map_query(self._original_query.end_before_document(document))

    def end_before(self, *args) -> Query[_T]:
        return self._map_query(self._original_query.end_before(*args))

    def get(self) -> QuerySnapshot[_T]:
        return WithConverterQuerySnapshot(self._original_query.get(), from_json=self._from_json, to_json=self._to_json)

    def limit(self, limit: int) -> Query[_T]:
        return self._map_query(self._original_query.limit(limit))

    def order_by(self, field: str | FieldPath, descending=False) -> Query[_T]:
        return self._map_query(self._original_query.order_by(field, descending))

    def start_after_document(self, document: DocumentSnapshot) -> Query[_T]:
        return self._map_query(self._original_query.start_after_document(document))

    def start_after(self, *args) -> Query[_T]:
        return self._map_query(self._original_query.start_after(*args))

    def start_at_document(self, document: DocumentSnapshot) -> Query[_T]:
        return self._map_query(self._original_query.start_at_document(document))

    def start_at(self, *args) -> Query[_T]:
        return self._map_query(self._original_query.start_at(*args))

    def limit_to_last(self, limit: int) -> Query[_T]:
        return self._map_query(self._original_query.limit_to_last(limit))

    def count(self) -> int:
        return self._original_query.count()

    def where(self, *args, **kwargs) -> Query[_T]:
        return self._map_query(self._original_query.where(*args, **kwargs))

    def exclude(self, *args, **kwargs) -> Query[_T]:
        return self._map_query(self._original_query.exclude(*args, **kwargs))

    def aggregate(self, *args) -> dict[str, Any]:
        return self._original_query.aggregate(*args)

    def with_converter(self, from_json: FromPyStoreDB[_U], to_json: ToPyStoreDB[_U]) -> Query[_T]:
        return WithConverterQuery(self._original_query, from_json, to_json)

    def __init__(self, original_query: Query[Json], from_json: FromPyStoreDB[_T], to_json: ToPyStoreDB[_T]):
        self._original_query = original_query
        self._from_json = from_json
        self._to_json = to_json


class WithConverterCollectionReference(WithConverterQuery[_T], CollectionReference[_T], Generic[_T]):

    def __init__(
            self,
            original_collection: CollectionReference[Json],
            from_json: FromPyStoreDB[_T],
            to_json: ToPyStoreDB[_T]
    ):
        super().__init__(original_collection, from_json, to_json)

    @property
    def _original_collection(self) -> CollectionReference[Json]:
        return cast(CollectionReference[Json], self._original_query)

    def with_converter(self, from_json: FromPyStoreDB[_U], to_json: ToPyStoreDB[_U]) -> CollectionReference[_T]:
        return WithConverterCollectionReference(self._original_collection, from_json, to_json)

    def doc(self, path: str = None) -> DocumentReference[_T]:
        return WithConverterDocumentReference(self._original_collection.doc(path), self._from_json, self._to_json)

    def add(self, data: _T) -> DocumentReference[_T]:
        data = self._to_json(data)
        return WithConverterDocumentReference(self._original_collection.add(data), self._from_json, self._to_json)

    @property
    def id(self) -> str:
        return self._original_collection.id

    @property
    def path(self) -> str:
        return self._original_collection.path
