from .._query import QueryDelegate
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
            import uuid
            path = uuid.uuid4().hex[:16]
        from PyStore.core._delegates.document import DocumentDelegate
        return DocumentDelegate(f'{self.path}/{path}', self.engine)
