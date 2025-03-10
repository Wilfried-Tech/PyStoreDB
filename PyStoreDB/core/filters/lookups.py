import abc
import operator
import re
from typing import Type

from PyStoreDB.constants import supported_types

__all__ = [
    'Lookup',
    'lookup_registry',
]


class __LookupRegistry:
    """Registry for managing lookup classes."""

    def __init__(self):
        """Initializes the lookup registry."""
        self.__registry: dict[type, dict[str, Type[Lookup]]] = {}

    def register(self, *field_types):
        """Decorator to register a lookup class. If no type is provided, it is generic.

        Args:
            *field_types: The field types to register the lookup for.

        Returns:
            function: The decorator function.
        """

        def decorator(lookup_cls):
            if not issubclass(lookup_cls, Lookup):
                raise TypeError(f'{lookup_cls} must be a subclass of {Lookup.__name__}')
            types = field_types or supported_types
            for field_type in types:
                self._add_lookup(field_type, lookup_cls)
            return lookup_cls  # Return the original class

        if field_types and issubclass(field_types[0], Lookup):
            cls, *field_types = field_types
            return decorator(cls)
        return decorator

    def _add_lookup(self, field_type, lookup_cls):
        """Adds a lookup for a specific type.

        Args:
            field_type: The field type to add the lookup for.
            lookup_cls: The lookup class to add.
        """
        self.__registry.setdefault(field_type, {})[lookup_cls.lookup_name] = lookup_cls

    def get_lookup(self, field_type, lookup_name, field_value, lookup_value):
        """Retrieves the lookup considering the 'i' prefix for strings.

        Args:
            field_type: The field type to retrieve the lookup for.
            lookup_name: The name of the lookup.
            field_value: The value of the field.
            lookup_value: The value to lookup.

        Returns:
            Lookup: The lookup instance or None if not found.
        """
        case_sensitive = True
        if (lookup_name.startswith("i") and len(lookup_name[1:]) > 1 and
                field_type == str and lookup_name[1:] in self.__registry.get(str, {})):
            lookup_name = lookup_name[1:]  # Remove the 'i'
            case_sensitive = False
        lookup_cls = self.__registry.get(field_type, dict()).get(lookup_name, None)
        if lookup_cls:
            return lookup_cls(field_value, lookup_value, case_sensitive)
        return None  # Lookup not found


class Lookup(abc.ABC):
    """Abstract base class for lookups."""

    lookup_name = None

    def __init__(self, db_value, value, case_sensitive=True):
        """Initializes the lookup.

        Args:
            db_value: The value from the database.
            value: The value to lookup.
            case_sensitive (bool): Whether the lookup is case sensitive. Defaults to True.
        """
        self.case_sensitive = case_sensitive
        self.db_value = db_value
        self.value = value
        self.db_value = self.prepare_db_value(db_value)
        self.value = self.prepare_value(value)
        self.prepare_lookup()
        if self.lookup_name is None:
            raise ValueError('lookup_name attribute must be set')

    def prepare_lookup(self):
        """Prepares the lookup. Can be overridden by subclasses."""
        pass

    def prepare_db_value(self, db_value):
        """Prepares the database value.

        Args:
            db_value: The value from the database.

        Returns:
            The prepared database value.
        """
        return db_value

    def prepare_value(self, value):
        """Prepares the lookup value.

        Args:
            value: The value to lookup.

        Returns:
            The prepared lookup value.
        """
        return value

    @property
    @abc.abstractmethod
    def as_bool(self) -> bool:
        """Evaluates the lookup as a boolean.

        Returns:
            bool: The result of the lookup.
        """
        pass

    def __bool__(self):
        """Evaluates the lookup as a boolean.

        Returns:
            bool: The result of the lookup.
        """
        return self.as_bool


lookup_registry = __LookupRegistry()


class BuiltinLookup(Lookup):
    """Builtin lookup class using operators."""

    _op = None

    @property
    def as_bool(self):
        """Evaluates the lookup using the operator.

        Returns:
            bool: The result of the lookup.

        Raises:
            NotImplementedError: If the operator is not implemented.
        """
        op = self._op or getattr(operator, self.lookup_name, None)
        if op is None:
            raise NotImplementedError(f"Operator {self.lookup_name} not implemented")
        return op(self.db_value, self.value)


@lookup_registry.register
class LessThan(BuiltinLookup):
    """Lookup class for less than comparison."""
    lookup_name = 'lt'


@lookup_registry.register
class LessThanEqual(BuiltinLookup):
    """Lookup class for less than or equal comparison."""
    _op = operator.le
    lookup_name = 'lte'


@lookup_registry.register
class GreaterThan(BuiltinLookup):
    """Lookup class for greater than comparison."""
    lookup_name = 'gt'


@lookup_registry.register
class GreaterThanEqual(BuiltinLookup):
    """Lookup class for greater than or equal comparison."""
    _op = operator.ge
    lookup_name = 'gte'


class StrPrepareMixin:
    """Mixin class for preparing string values."""

    def prepare_db_value(self, db_value):
        """Prepares the database value.

        Args:
            db_value: The value from the database.

        Returns:
            The prepared database value.
        """
        if isinstance(db_value, str):
            return str(db_value) if self.case_sensitive else str(db_value).lower()
        return db_value

    def prepare_value(self, value):
        """Prepares the lookup value.

        Args:
            value: The value to lookup.

        Returns:
            The prepared lookup value.
        """
        if isinstance(value, str):
            return str(value) if self.case_sensitive else str(value).lower()
        return value


@lookup_registry.register
class Exact(StrPrepareMixin, BuiltinLookup):
    """Lookup class for exact match comparison."""
    _op = operator.eq
    lookup_name = 'exact'


class PrepareListValueMixin(StrPrepareMixin):
    """Mixin class for preparing list values."""

    def prepare_list_value(self):
        """Prepares the list value.

        Returns:
            list: The prepared list value.
        """
        values = list(map(self.prepare_value, self.value))
        return values  # TODO evaluate values for potential F expressions


@lookup_registry.register
class In(PrepareListValueMixin, BuiltinLookup):
    """Lookup class for 'in' comparison."""
    lookup_name = 'in'

    @property
    def as_bool(self):
        """Evaluates the lookup using 'in' comparison.

        Returns:
            bool: The result of the lookup.
        """
        return self.db_value in self.prepare_list_value()


@lookup_registry.register
class IsNull(BuiltinLookup):
    """Lookup class for 'is null' comparison."""
    lookup_name = 'isnull'

    @property
    def as_bool(self):
        """Evaluates the lookup using 'is null' comparison.

        Returns:
            bool: The result of the lookup.

        Raises:
            ValueError: If the value is not a boolean.
        """
        if not isinstance(self.value, bool):
            raise ValueError('Value must be a boolean')
        return self.db_value is None if self.value else self.db_value is not None


class PatternLookup(Lookup):
    """Abstract base class for pattern-based lookups."""

    pattern: str | re.Pattern[str] = None

    def prepare_lookup(self):
        """Prepares the lookup by converting values to strings."""
        self.value = str(self.value)
        self.db_value = str(self.db_value)

    @property
    def as_bool(self):
        """Evaluates the lookup using a pattern.

        Returns:
            bool: The result of the lookup.

        Raises:
            ValueError: If the pattern is not specified.
        """
        if self.pattern is None:
            raise ValueError('pattern attribute must be specified')
        flag = 0 if self.case_sensitive else re.IGNORECASE
        pattern = self.pattern if isinstance(self.pattern, re.Pattern) else re.compile(
            self.pattern % (re.escape(self.value),)
        )
        return bool(re.search(pattern, self.db_value, flags=flag))


@lookup_registry.register
class StartsWith(PatternLookup):
    """Lookup class for 'starts with' comparison."""
    lookup_name = "startswith"
    pattern = '^%s'


@lookup_registry.register
class EndsWith(PatternLookup):
    """Lookup class for 'ends with' comparison."""
    lookup_name = "endswith"
    pattern = '%s$'


@lookup_registry.register
class Contains(PatternLookup):
    """Lookup class for 'contains' comparison."""
    lookup_name = "contains"
    pattern = '%s'


@lookup_registry.register
class Regex(PatternLookup):
    """Lookup class for regex comparison."""
    lookup_name = 'regex'

    def prepare_value(self, value):
        """Prepares the lookup value.

        Args:
            value: The value to lookup.

        Returns:
            The prepared lookup value.

        Raises:
            AssertionError: If the value is not a string or regex pattern.
        """
        assert isinstance(value, (str, re.Pattern)), f'{value} must be str or Pattern'
        self.pattern = value if isinstance(value, re.Pattern) else re.compile(value)
        return super().prepare_value(value)


@lookup_registry.register
class Range(Lookup, PrepareListValueMixin):
    """Lookup class for range comparison."""

    def prepare_value(self, value):
        """Prepares the lookup value.

        Args:
            value: The value to lookup.

        Raises:
            AssertionError: If the value is not a list, tuple, or set, or if its length is not 2.
        """
        assert isinstance(value, (list, tuple, set)), 'Value must be a list, tuple, or set'
        assert len(value) == 2, 'Value must contain exactly 2 elements'

    @property
    def as_bool(self) -> bool:
        """Evaluates the lookup using range comparison.

        Returns:
            bool: The result of the lookup.
        """
        return self.value[0] <= self.db_value <= self.value[1]
