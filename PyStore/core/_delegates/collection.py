from __future__ import annotations

from PyStore.engines import PyStoreEngine
from .._query import QueryDelegate
from ..._utils import generate_uuid


class CollectionDelegate(QueryDelegate):

    def __init__(self, path: str, engine: PyStoreEngine):
        super().__init__(path, engine)

    @property
    def id(self):
        return self.path.split('/')[-1]

    def doc(self, path: str | None):
        """

        :param path:
        :rtype: PyStore.core._delegates.document.DocumentDelegate
        """
        if path is None:
            path = generate_uuid()
        from PyStore.core._delegates.document import DocumentDelegate
        return DocumentDelegate(f'{self.path}/{path}', self.engine)
