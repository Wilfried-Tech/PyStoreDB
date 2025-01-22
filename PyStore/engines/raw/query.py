import operator
from operator import itemgetter
from typing import Callable, Any

from PyStore.engines import PyStoreEngine
from PyStore.query import FieldPath
from PyStore.types import Json


class PyStoreRawQuery:
    def __init__(self, engine: PyStoreEngine):
        self.engine = engine

    def apply_query_filters(self, data: dict[str, Json], **kwargs):
        if 'order_by' in kwargs:
            data = self._order_by(data, kwargs['order_by'])
        if 'limit' in kwargs:
            data = dict(list(data.items())[:kwargs.pop('limit')])
        elif 'limit_to_last' in kwargs:
            data = dict(list(data.items())[-kwargs.pop('limit_to_last'):])
        if 'start_at' in kwargs:
            data = self._by_cursor_value(
                data, kwargs['order_by'], kwargs.pop('start_at'),
                operator.ge, kwargs.pop('is_doc_cursor')
            )
        if 'start_after' in kwargs:
            data = self._by_cursor_value(
                data, kwargs['order_by'], kwargs.pop('start_after'),
                operator.gt, kwargs.pop('is_doc_cursor')
            )
        if 'end_at' in kwargs:
            data = self._by_cursor_value(
                data, kwargs['order_by'], kwargs.pop('end_at'),
                operator.le, kwargs.pop('is_doc_cursor')
            )
        if 'end_before' in kwargs:
            data = self._by_cursor_value(
                data, kwargs['order_by'], kwargs.pop('end_before'),
                operator.lt, kwargs.pop('is_doc_cursor')
            )

        return data

    def _order_by(self, data, orders: list[tuple[FieldPath, bool]]):
        data = self.to_data_list(data)
        for (_, item) in data:
            assert all([
                str(order[0]) in item
                for order in orders
                if order[0] != FieldPath.document_id]), 'order_by field must be present in all documents'
            assert all([not isinstance(item[str(order[0])], (dict, list)) for order in orders
                        if order[0] != FieldPath.document_id]), 'order_by fields value must not be a dict or list'

        for field, descending in orders[::-1]:
            data = sorted(
                data,
                key=self._get_field_value(field),
                reverse=descending
            )
        return dict(data)

    @staticmethod
    def to_data_list(data: dict):
        return [(k, v) for k, v in data.items()]

    @staticmethod
    def _get_field_value(field: FieldPath):
        def key_func(item):
            if field == FieldPath.document_id:
                return item[0]
            return item[1][str(field)]

        return key_func

    @staticmethod
    def _filter_by_key_value_func(field: FieldPath, op: Callable, value):
        def key_func(item):
            db_value = PyStoreRawQuery._get_field_value(field)(item)
            assert type(db_value) is type(value), ('value type of fields in order_by clauses must match in order '
                                                   'values in start_after(), start_at(), end_before(), end_at()')
            return op(db_value, value)

        return key_func

    def _by_cursor_value(self, data, orders, values, op: Callable[[Any, Any], bool], is_doc: bool):
        keypair = list(zip(map(itemgetter(0), orders), list(values)))
        data = self.to_data_list(data)
        if is_doc:
            return self._by_document_cursor(keypair, data, op)
        for field, value in keypair:
            data = list(
                filter(self._filter_by_key_value_func(field, op, value), data)
            )
        return dict(data)

    def _by_document_cursor(self, keypair: list[tuple[FieldPath, Any]], data: list[tuple[str, Any]],
                            op: Callable[[Any, Any], bool]):

        for index, item in enumerate(data):
            if all([self._get_field_value(field)(item) == value for field, value in keypair]):
                if op == operator.gt:
                    return dict(data[index + 1:])
                elif op == operator.ge:
                    return dict(data[index:])
                elif op == operator.lt:
                    return dict(data[:index])
                elif op == operator.le:
                    return dict(data[:index + 1])
                break
        return dict(data)
