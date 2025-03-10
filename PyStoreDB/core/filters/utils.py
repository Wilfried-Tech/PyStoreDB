from __future__ import annotations

from typing import Any

__all__ = ['F', 'Q']


class F:
    """Class to represent a field in a document.

    Attributes:
        field (str): The name of the field.
    """

    def __init__(self, field: str):
        """Initializes the F object with a field name.

        Args:
            field (str): The name of the field.
        """
        self.field = field

    def resolve(self, document: dict[str, Any]) -> Any:
        """Resolves the value of the field in the given document.

        Args:
            document (dict[str, Any]): The document to resolve the field from.

        Returns:
            Any: The value of the field in the document.

        Raises:
            AssertionError: If the field is not found in the document.
        """
        assert self.field in document, f"Field {self.field} not found in document"
        return document[self.field]

    def __repr__(self):
        """Returns a string representation of the F object.

        Returns:
            str: String representation of the F object.
        """
        return f"<F: {self.field}>"


class Q:
    """Class to represent a query with logical conditions.

    Attributes:
        AND (str): Logical AND connector.
        OR (str): Logical OR connector.
        XOR (str): Logical XOR connector.
        default_connector (str): Default logical connector.
        children (list): List of child conditions.
        connector (str): Logical connector for the query.
        negated (bool): Whether the query is negated.
    """
    AND = 'AND'
    OR = 'OR'
    XOR = 'XOR'
    default_connector = AND

    def __init__(self, *args: Q, connector=None, negated=False, **kwargs):
        """Initializes the Q object with conditions and logical connector.

        Args:
            *args (Q): Positional arguments representing child conditions.
            connector (str, optional): Logical connector for the query. Defaults to None.
            negated (bool, optional): Whether the query is negated. Defaults to False.
            **kwargs: Keyword arguments representing child conditions.
        """
        self.children = list(args) + list(kwargs.items())
        self.connector = connector or self.default_connector
        self.negated = negated

    def _combine(self, other, conn):
        """Combines the current query with another query using the specified connector.

        Args:
            other (Q): The other query to combine with.
            conn (str): The logical connector to use.

        Returns:
            Q: The combined query.

        Raises:
            TypeError: If the other object is not a Q instance.
        """
        if not isinstance(other, Q):
            raise TypeError(other)
        if not other and isinstance(other, Q):
            return self.copy()
        obj = Q(connector=conn)
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def add(self, data, conn_type):
        """Adds a condition to the query.

        Args:
            data: The condition to add.
            conn_type (str): The logical connector to use.

        Returns:
            Q: The updated query.
        """
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
        """Creates a copy of the query.

        Returns:
            Q: The copied query.
        """
        obj = Q(*self.children, connector=self.connector, negated=self.negated)
        return obj

    copy = __copy__

    def __len__(self):
        """Returns the number of child conditions.

        Returns:
            int: The number of child conditions.
        """
        return len(self.children)

    def __bool__(self):
        """Evaluates the query as a boolean.

        Returns:
            bool: True if the query has child conditions, False otherwise.
        """
        return bool(self.children)

    def __and__(self, other):
        """Combines the query with another query using the AND connector.

        Args:
            other (Q): The other query to combine with.

        Returns:
            Q: The combined query.
        """
        return self._combine(other, self.AND)

    def __or__(self, other):
        """Combines the query with another query using the OR connector.

        Args:
            other (Q): The other query to combine with.

        Returns:
            Q: The combined query.
        """
        return self._combine(other, self.OR)

    def __xor__(self, other):
        """Combines the query with another query using the XOR connector.

        Args:
            other (Q): The other query to combine with.

        Returns:
            Q: The combined query.
        """
        return self._combine(other, self.XOR)

    def __invert__(self):
        """Negates the query.

        Returns:
            Q: The negated query.
        """
        obj = self.copy()
        obj.negated = not obj.negated
        return obj

    def __str__(self):
        """Returns a string representation of the query.

        Returns:
            str: String representation of the query.
        """
        template = '(NOT (%s: %s))' if self.negated else '(%s: %s)'
        return template % (self.connector, ', '.join(map(str, self.children)))

    def __repr__(self):
        """Returns a string representation of the query for debugging.

        Returns:
            str: String representation of the query.
        """
        return f"<Q: {self}>"
