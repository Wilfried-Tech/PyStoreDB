from __future__ import annotations

from PyStore.core._delegates.collection import CollectionDelegate
from PyStore.core._delegates.document import DocumentDelegate
from PyStore.engines import PyStoreEngine
from PyStore._utils import is_valid_document, validate_path, is_valid_collection

__all__ = ['StoreDelegate', 'CollectionDelegate', 'DocumentDelegate']


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
