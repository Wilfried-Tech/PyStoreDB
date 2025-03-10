from __future__ import annotations

from typing import Any

__all__ = ['F', 'Q']


class F:

    def __init__(self, field: str):
        self.field = field

    def resolve(self, document: dict[str, Any]) -> Any:
        assert self.field in document, f"Field {self.field} not found in document"
        return document[self.field]

    def __repr__(self):
        return f"<F: {self.field}>"


class Q:
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'
    default_connector = AND

    def __init__(self, *args: Q, connector=None, negated=False, **kwargs):
        self.children = list(args) + list(kwargs.items())
        self.connector = connector or self.default_connector
        self.negated = negated

    def _combine(self, other, conn):
        if not isinstance(other, Q):
            raise TypeError(other)
        if not other and isinstance(other, Q):
            return self.copy()
        obj = Q(connector=conn)
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def add(self, data, conn_type):
        if not data:
            return self
        if self.connector != conn_type:
            obj = self.copy()
            self.connector = conn_type
            self.children = [obj, data]
            return data
        elif (
                isinstance(data, Q)
                and not data.negated
                and (data.connector == conn_type or len(data) == 1)
        ):
            self.children.extend(data.children)
            return self
        else:
            self.children.append(data)
            return data

    def __copy__(self):
        obj = Q(*self.children, connector=self.connector, negated=self.negated)
        return obj

    copy = __copy__

    def __len__(self):
        return len(self.children)

    def __bool__(self):
        return bool(self.children)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __xor__(self, other):
        return self._combine(other, self.XOR)

    def __invert__(self):
        obj = self.copy()
        obj.negated = not obj.negated
        return obj

    def __str__(self):
        template = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return template % (self.connector, ', '.join(map(str, self.children)))

    def __repr__(self):
        return f"<Q: {self}>"
