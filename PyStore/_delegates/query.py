from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyStore.engines import PyStoreEngine


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
