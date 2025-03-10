from PyStoreDB.constants import Json, LOOKUP_SEP
from PyStoreDB.core.filters.lookups import Lookup, lookup_registry
from PyStoreDB.core.filters.utils import Q, F

__all__ = ['Q', 'F', 'Lookup', 'lookup_registry', 'FilteredQuery']


class FilteredQuery:
    """Class to handle filtered queries on data.

    Attributes:
        data (list[tuple[str, Json]]): The data to be filtered.
        filters (list[Q]): The list of filters to apply.
        _len (int): The length of the data.
        _index (int): The current index in the iteration.
        _current (tuple[str, Json]): The current row being processed.
    """

    def __init__(self, data: list[tuple[str, Json]], filters: list[Q]):
        """Initializes the FilteredQuery with data and filters.

        Args:
            data (list[tuple[str, Json]]): The data to be filtered.
            filters (list[Q]): The list of filters to apply.
        """
        self.data = data
        self.filters = filters
        self._len = len(data)
        self._index = 0
        self._current = None

    def __iter__(self):
        """Resets the iterator and returns the iterator object.

        Returns:
            FilteredQuery: The iterator object.
        """
        self._index = 0
        self._current = None
        return self

    def __next__(self):
        """Returns the next filtered row in the data.

        Returns:
            tuple[str, Json]: The next filtered row.

        Raises:
            StopIteration: If there are no more rows to iterate.
        """
        while self._index < self._len:
            row = self.data[self._index]
            self._index += 1
            res = self._apply_filters(row)
            if res:
                return res
        raise StopIteration

    def _apply_filters(self, row: tuple[str, Json]):
        """Applies the filters to a row.

        Args:
            row (tuple[str, Json]): The row to be filtered.

        Returns:
            tuple[str, Json] or None: The row if it matches all filters, otherwise None.
        """
        conditions = []
        self._current = row
        for q in self.filters:
            res = self._add_q(q)
            conditions.append(res)
        return row if all(conditions) else None

    def _add_q(self, q: Q):
        """Adds a Q object filter to the conditions.

        Args:
            q (Q): The Q object containing the filter conditions.

        Returns:
            bool: The result of applying the Q object filter.
        """
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
        """Builds a filter from a child condition.

        Args:
            child: The child condition to build the filter from.

        Returns:
            bool: The result of applying the filter.
        """
        if isinstance(child, Q):
            return self._add_q(child)
        arg, value = child
        if not arg:
            raise ValueError('Cannot parse query keyword {}'.format(arg))
        value = self._resolve_value(value)
        lookup = self._build_lookup(arg, value)
        return lookup.as_bool

    def _resolve_value(self, value):
        """Resolves the value for a filter condition.

        Args:
            value: The value to resolve.

        Returns:
            The resolved value.
        """
        if isinstance(value, F):
            return value.resolve(self._current[1])
        elif isinstance(value, (list, tuple)):
            return [self._resolve_value(v) for v in value]
        return value

    def _build_lookup(self, arg, value):
        """Builds a lookup object for a filter condition.

        Args:
            arg: The argument for the lookup.
            value: The value for the lookup.

        Returns:
            Lookup: The lookup object.

        Raises:
            ValueError: If the field is not found in the document or the lookup is not found.
        """
        field, _, lookup_name = arg.partition(LOOKUP_SEP)
        if field not in self._current[1]:
            raise ValueError(f'Field {field} not found in document')
        db_value = self._current[1][field]
        lookup_name = lookup_name or 'exact'
        lookup = lookup_registry.get_lookup(type(db_value), lookup_name, db_value, value)
        if lookup is None:
            raise ValueError(f'Lookup "{lookup_name}" not found for field "{field}"')
        return lookup
