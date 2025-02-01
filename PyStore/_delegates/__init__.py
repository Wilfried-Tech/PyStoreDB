from __future__ import annotations

from typing import TYPE_CHECKING

from PyStore._delegates.collection import CollectionDelegate
from PyStore._delegates.document import DocumentDelegate
from PyStore._delegates.query import QueryDelegate
from PyStore._utils import is_valid_document, validate_path, is_valid_collection

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
