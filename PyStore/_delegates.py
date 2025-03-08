from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

from PyStore._utils import is_valid_document, validate_path, is_valid_collection, generate_uuid, parent_path
from PyStore.constants import Json
from PyStore.core import FieldPath

if TYPE_CHECKING:
    from PyStore.engines import PyStoreEngine

__all__ = ['StoreDelegate', 'CollectionDelegate', 'DocumentDelegate', 'QueryDelegate']


class StoreDelegate:

    def __init__(self, engine: PyStoreEngine):
        self.engine = engine

    def collection(self, path: str) -> CollectionDelegate:
        if not path.startswith('/'):
            path = '/' + path
        validate_path(path)
        is_valid_collection(path)
        return CollectionDelegate(path, self.engine)

    def doc(self, path: str) -> DocumentDelegate:
        if not path.startswith('/'):
            path = '/' + path
        validate_path(path)
        is_valid_document(path)
        return DocumentDelegate(path, self.engine)


class DocumentDelegate:

    def __init__(self, path: str, engine: PyStoreEngine):
        self.path = path
        self.engine = engine

    @property
    def id(self):
        return self.path.split('/')[-1]

    @property
    def exists(self) -> bool:
        return self.engine.path_exists(self.path) and is_valid_document(self.path) and self.engine.doc_exists(self.path)

    @property
    def parent(self):
        path = parent_path(self.path)
        if path:
            return CollectionDelegate(path, self.engine)
        return None

    def collection(self, path: str):
        return CollectionDelegate(f'{self.path}/{path}', self.engine)

    def set(self, data: Json):
        self.engine.set(self.path, data)

    def delete(self):
        if self.exists:
            self.engine.delete(self.path)
        else:
            warnings.warn(f"Document {self.path} does not exist")

    def get(self):
        return DocumentDelegate(self.path, self.engine)

    def update(self, data: Json):
        self.engine.update(self.path, data)

    def get_field(self, field: str | FieldPath, default=None) -> Any:
        if self.exists:
            return self.engine.get_field(self.path, field, default)
        warnings.warn(f"Document {self.path} does not exist")
        return default

    def data(self) -> Json | None:
        if self.exists:
            return self.engine.get_document(self.path)

        warnings.warn(f"Document {self.path} does not exist")
        return None


class QueryDelegate:

    def __init__(self, path: str, engine: PyStoreEngine, **kwargs):
        self.path = path
        self.engine = engine
        self.kwargs = kwargs

    def _copy(self, **kwargs):
        return QueryDelegate(path=self.path, engine=self.engine, **{**self.kwargs, **kwargs})

    def get(self, path: str):
        return self._copy(path=path)

    def limit(self, limit):
        return self._copy(limit=limit)

    def order_by(self, orders: list[tuple[str, bool]]):
        return self._copy(order_by=orders)

    def limit_to_last(self, limit):
        return self._copy(limit_to_last=limit)

    def start_at(self, *args):
        return self._copy(start_at=args, is_doc_cursor=False)

    def start_after(self, *args):
        return self._copy(start_after=args, is_doc_cursor=False)

    def end_at(self, *args):
        return self._copy(end_at=args, is_doc_cursor=False)

    def end_before(self, *args):
        return self._copy(end_before=args, is_doc_cursor=False)

    def start_at_document(self, orders, values):
        return self._copy(order_by=orders, start_at=values, is_doc_cursor=True)

    def start_after_document(self, orders, values):
        return self._copy(order_by=orders, start_after=values, is_doc_cursor=True)

    def end_at_document(self, orders, values):
        return self._copy(order_by=orders, end_at=values, is_doc_cursor=True)

    def end_before_document(self, orders, values):
        return self._copy(order_by=orders, end_before=values, is_doc_cursor=True)

    def where(self, filters):
        return self._copy(filters=filters)


class CollectionDelegate(QueryDelegate):

    def __init__(self, path: str, engine: PyStoreEngine):
        super().__init__(path, engine)

    @property
    def id(self):
        return self.path.split('/')[-1]

    def doc(self, path: str | None):
        if path is None:
            path = generate_uuid()
        return DocumentDelegate(f'{self.path}/{path}', self.engine)
