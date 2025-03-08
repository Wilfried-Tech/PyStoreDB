from PyStore.constants import Json, LOOKUP_SEP
from PyStore.core.filters.lookups import Lookup, lookup_registry
from PyStore.core.filters.utils import Q, F

__all__ = ['Q', 'F', 'Lookup', 'lookup_registry', 'FilteredQuery']


class FilteredQuery:
    def __init__(self, data: list[tuple[str, Json]], filters: list[Q]):
        self.data = data
        self.filters = filters
        self._len = len(data)
        self._index = 0
        self._current = None

    def __iter__(self):
        self._index = 0
        self._current = None
        print(f'Filters: {self.filters}')
        return self

    def __next__(self):
        while self._index < self._len:
            row = self.data[self._index]
            self._index += 1
            res = self._apply_filters(row)
            if res:
                return res
        raise StopIteration

    def _apply_filters(self, row: tuple[str, Json]):
        conditions = []
        self._current = row
        for q in self.filters:
            res = self._add_q(q)
            conditions.append(res)
        return row if all(conditions) else None

    def _add_q(self, q: Q):
        conditions = []
        for child in q.children:
            res = self._build_filter(child)
            conditions.append(res)
        if q.connector == Q.AND:
            return all(conditions) ^ q.negated
        elif q.connector == Q.OR:
            return any(conditions) ^ q.negated
        elif q.connector == Q.XOR:
            return (sum(conditions) == 1) ^ q.negated
        raise ValueError(f'Unknown connector {q.connector}')

    def _build_filter(self, child):
        if isinstance(child, Q):
            return self._add_q(child)
        arg, value = child
        if not arg:
            raise ValueError('Cannot parse query keyword {}'.format(arg))
        value = self._resolve_value(value)
        lookup = self._build_lookup(arg, value)
        return lookup.as_bool

    def _resolve_value(self, value):
        if isinstance(value, F):
            return value.resolve(self._current[1])
        elif isinstance(value, (list, tuple)):
            return [self._resolve_value(v) for v in value]
        return value

    def _build_lookup(self, arg, value):
        field, _, lookup_name = arg.partition(LOOKUP_SEP)
        if field not in self._current[1]:
            raise ValueError(f'Field {field} not found in document')
        db_value = self._current[1][field]
        lookup_name = lookup_name or 'exact'
        lookup = lookup_registry.get_lookup(type(db_value), lookup_name, db_value, value)
        if lookup is None:
            raise ValueError(f'Lookup "{lookup_name}" not found for field "{field}"')
        return lookup
