from __future__ import annotations

from typing import TYPE_CHECKING

from PyStore._utils import generate_uuid
from .query import QueryDelegate

if TYPE_CHECKING:
    from PyStore.engines import PyStoreEngine


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
        from PyStore._delegates import DocumentDelegate
        return DocumentDelegate(f'{self.path}/{path}', self.engine)
