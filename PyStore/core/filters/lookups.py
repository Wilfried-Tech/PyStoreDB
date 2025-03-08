import abc
import operator
import re
from typing import Type

from PyStore.constants import supported_types

__all__ = [
    'Lookup',
    'lookup_registry',
]


class __LookupRegistry:
    def __init__(self):
        self.__registry: dict[type, dict[str, Type[Lookup]]] = {}

    def register(self, *field_types):
        """Décorateur pour enregistrer un lookup. S'il n'y a pas de type, il est générique."""

        def decorator(lookup_cls):
            if not issubclass(lookup_cls, Lookup):
                raise TypeError(f'{lookup_cls} must be a subclass of {Lookup.__name__}')
            types = field_types or supported_types
            for field_type in types:
                self._add_lookup(field_type, lookup_cls)
            return lookup_cls  # Retourner la classe originale

        if field_types and issubclass(field_types[0], Lookup):
            cls, *field_types = field_types
            return decorator(cls)
        return decorator

    def _add_lookup(self, field_type, lookup_cls):
        """Ajoute un lookup pour un type spécifique."""
        self.__registry.setdefault(field_type, {})[lookup_cls.lookup_name] = lookup_cls

    def get_lookup(self, field_type, lookup_name, field_value, lookup_value):
        """Récupère le lookup en tenant compte du préfixe 'i' pour les chaînes."""
        case_sensitive = True

        # print(field_type, lookup_name, field_value, lookup_value)

        if (lookup_name.startswith("i") and len(lookup_name[1:]) > 1 and
                field_type == str and lookup_name[1:] in self.__registry.get(str, {})):
            lookup_name = lookup_name[1:]  # Retire le 'i'
            case_sensitive = False
        lookup_cls = self.__registry.get(field_type, dict()).get(lookup_name, None)
        if lookup_cls:
            return lookup_cls(field_value, lookup_value, case_sensitive)
        return None  # Lookup non trouvé


class Lookup(abc.ABC):
    lookup_name = None

    def __init__(self, db_value, value, case_sensitive=True):
        self.case_sensitive = case_sensitive
        self.db_value = db_value
        self.value = value
        self.db_value = self.prepare_db_value(db_value)
        self.value = self.prepare_value(value)
        self.prepare_lookup()
        if self.lookup_name is None:
            raise ValueError('lookup_name attribute must be set')

    def prepare_lookup(self):
        pass

    def prepare_db_value(self, db_value):
        return db_value

    def prepare_value(self, value):
        return value

    @property
    @abc.abstractmethod
    def as_bool(self) -> bool:
        pass

    def __bool__(self):
        return self.as_bool


lookup_registry = __LookupRegistry()


class BuiltinLookup(Lookup):
    _op = None

    @property
    def as_bool(self):
        op = self._op or getattr(operator, self.lookup_name, None)
        if op is None:
            raise NotImplementedError(f"Operator {self.lookup_name} not implemented")
        return op(self.db_value, self.value)


@lookup_registry.register
class LessThan(BuiltinLookup):
    lookup_name = 'lt'


@lookup_registry.register
class LessThanEqual(BuiltinLookup):
    _op = operator.le
    lookup_name = 'lte'


@lookup_registry.register
class GreaterThan(BuiltinLookup):
    lookup_name = 'gt'


@lookup_registry.register
class GreaterThanEqual(BuiltinLookup):
    _op = operator.ge
    lookup_name = 'gte'


class StrPrepareMixin:
    def prepare_db_value(self, db_value):
        if isinstance(db_value, str):
            return str(db_value) if self.case_sensitive else str(db_value).lower()
        return db_value

    def prepare_value(self, value):
        if isinstance(value, str):
            return str(value) if self.case_sensitive else str(value).lower()
        return value


@lookup_registry.register
class Exact(StrPrepareMixin, BuiltinLookup):
    _op = operator.eq
    lookup_name = 'exact'


class PrepareListValueMixin(StrPrepareMixin):

    def prepare_list_value(self):
        values = list(map(self.prepare_value, self.value))
        return values  # TODO evaluate values for potential F expressions


@lookup_registry.register
class In(PrepareListValueMixin, BuiltinLookup):
    lookup_name = 'in'

    @property
    def as_bool(self):
        return self.db_value in self.prepare_list_value()


@lookup_registry.register
class IsNull(BuiltinLookup):
    lookup_name = 'isnull'

    @property
    def as_bool(self):
        if not isinstance(self.value, bool):
            raise ValueError('Value must be a boolean')
        return self.db_value is None if self.value else self.db_value is not None


class PatternLookup(Lookup):
    pattern: str | re.Pattern[str] = None

    def prepare_lookup(self):
        self.value = str(self.value)
        self.db_value = str(self.db_value)

    @property
    def as_bool(self):
        if self.pattern is None:
            raise ValueError('pattern attribute must be specified')
        flag = 0 if self.case_sensitive else re.IGNORECASE
        pattern = self.pattern if isinstance(self.pattern, re.Pattern) else re.compile(
            self.pattern % (re.escape(self.value),)
        )
        return bool(re.search(pattern, self.db_value, flags=flag))


@lookup_registry.register
class StartsWith(PatternLookup):
    lookup_name = "startswith"
    pattern = '^%s'


@lookup_registry.register
class EndsWith(PatternLookup):
    lookup_name = "endswith"
    pattern = '%s$'


@lookup_registry.register
class Contains(PatternLookup):
    lookup_name = "contains"
    pattern = '%s'


@lookup_registry.register
class Regex(PatternLookup):
    lookup_name = 'regex'

    def prepare_value(self, value):
        assert isinstance(value, (str, re.Pattern)), f'{value} must be str or Pattern'
        self.pattern = value if isinstance(value, re.Pattern) else re.compile(value)
        return super().prepare_value(value)


@lookup_registry.register
class Range(Lookup, PrepareListValueMixin):

    def prepare_value(self, value):
        assert isinstance(value, (list, tuple, set)), ''
        assert len(value) == 2, ''

    @property
    def as_bool(self) -> bool:
        return self.value[0] <= self.value[0] <= self.db_value
