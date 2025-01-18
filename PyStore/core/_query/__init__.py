from __future__ import annotations

from typing import TYPE_CHECKING

from PyStore.types import Json
from .delegate import QueryDelegate
from .field_path import FieldPath
from .query import Query
from .query_snapshot import QuerySnapshot, JsonQuerySnapshot

__all__ = ['Query', 'QuerySnapshot', 'JsonQuery', 'JsonQuerySnapshot', 'QueryDelegate']

if TYPE_CHECKING:
    from .._common import DocumentSnapshot


class JsonQuery(Query[Json]):

    def count(self) -> int:
        return self.get().size

    def get(self) -> QuerySnapshot[Json]:
        return JsonQuerySnapshot(self._delegate)

    def limit(self, limit: int) -> JsonQuery[Json]:
        assert limit > 0, 'limit must be a positive number greater than 0'
        return JsonQuery(self._delegate.limit(limit))

    def order_by(self, field: str | FieldPath, descending=False) -> JsonQuery[Json]:
        self._assert_valid_field_type(field)

        assert not self._has_start_cursor(), '''Invalid query. You must not call start_after(), start_at(), start_at_document(), '
        start_after_document() before calling order_by()'''

        assert not self._has_end_cursor(), '''Invalid query. You must not call end_before(), end_at() end_at_document(), '
        end_before_document() after calling order_by()'''

        orders = self._parameters.get('order_by', list())

        assert len([item == field for item in orders]) == 0, f'order by field "{field}" already exists in query'

        if isinstance(field, FieldPath):
            orders.append((field, descending))
        elif field == FieldPath.document_id:
            orders.append((FieldPath.document_id, descending))
        else:
            orders.append((FieldPath(field), descending))

        return JsonQuery(self._delegate.order_by(orders))

    def limit_to_last(self, limit: int) -> JsonQuery[Json]:
        assert limit > 0, 'limit must be a positive number greater than 0'
        orders = list(self._parameters['order_by'])
        assert len(orders) > 0, 'limit_to_last queries require specifying at least one order_by() clause'

        return JsonQuery(self._delegate.limit_to_last(limit))

    def where(self, **kwargs) -> JsonQuery[Json]:
        pass

    def aggregate(self, *args) -> JsonQuery[Json]:
        pass

    def end_at(self, *args) -> JsonQuery[Json]:
        pass

    def end_at_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        pass

    def end_before(self, *args) -> JsonQuery[Json]:
        pass

    def end_before_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        pass

    def start_after(self, *args) -> JsonQuery[Json]:
        pass

    def start_after_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        pass

    def start_at(self, *args) -> JsonQuery[Json]:
        pass

    def start_at_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        pass

    def __init__(self, query_delegate: QueryDelegate):
        self._delegate = query_delegate

    @property
    def _parameters(self):
        return self._delegate.parameters

    def _has_start_cursor(self):
        return 'start_at' in self._parameters or 'start_after' in self._parameters

    def _has_end_cursor(self):
        return 'end_at' in self._parameters or 'end_before' in self._parameters

    @staticmethod
    def _assert_valid_field_type(field):
        assert isinstance(field, str) or isinstance(field, FieldPath), 'field must be a string or FieldPath'
