from __future__ import annotations

from typing import Any

from PyStore._delegates import QueryDelegate
from PyStore.constants import Json
from PyStore.core import Query, QuerySnapshot, FieldPath, DocumentSnapshot

__all__ = ['JsonQuery']

from PyStore.core.aggregate import Aggregation

from PyStore.core.filters import Q


class JsonQuery(Query[Json]):

    def count(self) -> int:
        return self.get().size

    def get(self) -> QuerySnapshot[Json]:
        from PyStore._impl import JsonQuerySnapshot
        return JsonQuerySnapshot(self._delegate)

    def limit(self, limit: int) -> JsonQuery[Json]:
        assert limit > 0, 'limit must be a positive number greater than 0'
        assert 'limit_to_last' not in self._kwargs, 'Invalid query. You cannot call limit() after limit_to_last(), these are mutually exclusive'

        return JsonQuery(self._delegate.limit(limit))

    def order_by(self, field: str | FieldPath, descending=False) -> JsonQuery[Json]:
        self._assert_valid_field_type(field)

        assert not self._has_start_cursor(), '''Invalid query. You must not call start_after(), start_at(), start_at_document(), '
        start_after_document() before calling order_by()'''

        assert not self._has_end_cursor(), '''Invalid query. You must not call end_before(), end_at() end_at_document(), '
        end_before_document() before calling order_by()'''

        orders = list(self._kwargs.get('order_by', []))
        assert all([item != field for item in orders]), f'order by field "{field}" already exists in query'

        if isinstance(field, FieldPath):
            orders.append((field, descending))
        elif field == FieldPath.document_id:
            orders.append((FieldPath.document_id, descending))
        else:
            orders.append((FieldPath(field), descending))

        return JsonQuery(self._delegate.order_by(orders))

    def limit_to_last(self, limit: int) -> JsonQuery[Json]:
        assert limit > 0, 'limit must be a positive number greater than 0'
        orders = list(self._kwargs['order_by'])
        assert len(orders) > 0, 'limit_to_last queries require specifying at least one order_by() clause'
        assert 'limit' not in self._kwargs, 'Invalid query. You cannot call limit_to_last() after limit(), these are mutually exclusive'

        return JsonQuery(self._delegate.limit_to_last(limit))

    def start_at(self, *args) -> JsonQuery[Json]:
        self._assert_query_cursor_values(args)
        return JsonQuery(self._delegate.start_at(*args))

    def start_after(self, *args) -> JsonQuery[Json]:
        self._assert_query_cursor_values(args)
        return JsonQuery(self._delegate.start_after(*args))

    def end_at(self, *args) -> JsonQuery[Json]:
        self._assert_query_cursor_values(args)
        return JsonQuery(self._delegate.end_at(*args))

    def end_before(self, *args) -> JsonQuery[Json]:
        self._assert_query_cursor_values(args)
        return JsonQuery(self._delegate.end_before(*args))

    def start_at_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        orders, values = self._assert_query_cursor_snapshot(document)
        return JsonQuery(self._delegate.start_at_document(orders, values))

    def start_after_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        orders, values = self._assert_query_cursor_snapshot(document)
        return JsonQuery(self._delegate.start_after_document(orders, values))

    def end_at_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        orders, values = self._assert_query_cursor_snapshot(document)
        return JsonQuery(self._delegate.end_at_document(orders, values))

    def end_before_document(self, document: DocumentSnapshot) -> JsonQuery[Json]:
        orders, values = self._assert_query_cursor_snapshot(document)
        return JsonQuery(self._delegate.end_before_document(orders, values))

    def where(self, *args, **kwargs) -> JsonQuery[Json]:
        _filters = list(self._kwargs.get('filters', []))
        _filters.extend([Q(*args, **kwargs)])
        return JsonQuery(self._delegate.where(_filters))

    def exclude(self, *args, **kwargs) -> JsonQuery[Json]:
        _filters = list(self._kwargs.get('filters', []))
        _filters.extend([Q(*args, **kwargs, negated=True)])
        return JsonQuery(self._delegate.where(_filters))

    def aggregate(self, mapping: dict[str, Aggregation] = None, **kwargs) -> dict[str, Any]:
        if mapping is None:
            mapping = {}
        mapping = {**mapping, **kwargs}
        data = self.get().docs
        return {key: aggregation.apply(data) for key, aggregation in mapping.items()}

    def __init__(self, query_delegate: QueryDelegate):
        self._delegate = query_delegate

    @property
    def _kwargs(self):
        return self._delegate.kwargs

    def _has_start_cursor(self):
        return 'start_at' in self._kwargs or 'start_after' in self._kwargs

    def _has_end_cursor(self):
        return 'end_at' in self._kwargs or 'end_before' in self._kwargs

    @staticmethod
    def _assert_valid_field_type(field):
        assert isinstance(field, str) or isinstance(field, FieldPath), 'field must be a string or FieldPath'

    def _assert_query_cursor_values(self, fields: list | tuple):
        assert len(fields) <= len(self._kwargs.get('order_by', list())), \
            'Too many arguments provided. ' \
            'The number of arguments must be less than or equal to the number of order_by() clauses.'

    def _assert_query_cursor_snapshot(self, _snapshot: DocumentSnapshot) -> tuple[list, list]:
        assert _snapshot.exists, 'Invalid query. The document must exist to be used in a query'
        assert _snapshot.reference.parent.path == self._delegate.path, 'Invalid query. The document must belong to the same collection as the query'

        orders = list(self._kwargs.get('order_by', list()))
        values = []

        for order in orders:
            if order[0] != FieldPath.document_id:
                try:
                    value = _snapshot.get(str(order[0]))
                    if value is None:
                        raise KeyError
                    values.append(value)  # TODO check this when support map and list lookup
                except KeyError:
                    raise ValueError(
                        "You are trying to start or end a query using a document for"
                        f" which the field '{order[0]}' (used as the order_by) does not exist."
                    )

        # automatically add FieldPath.document_id to orders if is not the last
        if len(orders) != 0:
            last_order = orders[-1]
            if last_order[0] != FieldPath.document_id:
                orders.append((FieldPath.document_id, last_order[1]))
        else:
            orders.append((FieldPath.document_id, False))

        values.append(_snapshot.id)

        return orders, values
