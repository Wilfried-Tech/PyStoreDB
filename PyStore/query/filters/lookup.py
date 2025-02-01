import abc
import operator
from typing import Type

from PyStore.types import supported_types


class _LookupRegistry:
    def __init__(self):
        self.__registry: dict[type, dict[str, Type[Lookup]]] = {}

    def register(self, *field_types):
        """Décorateur pour enregistrer un lookup. S'il n'y a pas de type, il est générique."""

        def decorator(lookup_cls):
            if not issubclass(lookup_cls, Lookup):
                raise TypeError(f'{lookup_cls} must be a subclass of {Lookup.__name__}')
            if not field_types:  # Si aucun type n'est fourni, enregistrer pour tous les types
                for field_type in supported_types:
                    self._add_lookup(field_type, lookup_cls)
            else:
                for field_type in field_types:
                    self._add_lookup(field_type, lookup_cls)
            return lookup_cls  # Retourner la classe originale

        if field_types and issubclass(field_types[0], Lookup):
            cls, *field_types = field_types
            return decorator(cls)
        return decorator

    def _add_lookup(self, field_type, lookup_cls):
        """Ajoute un lookup pour un type spécifique."""
        if field_type not in self.__registry:
            self.__registry[field_type] = {}
        self.__registry[field_type][lookup_cls.lookup_name] = lookup_cls

    def get_lookup(self, field_type, lookup_name, field_value, lookup_value):
        """Récupère le lookup en tenant compte du préfixe 'i' pour les chaînes."""
        case_sensitive = True

        if lookup_name.startswith("i") and field_type == str and lookup_name[1:] in self.__registry.get(str, {}):
            lookup_name = lookup_name[1:]  # Retire le 'i'
            case_sensitive = False

        lookup_cls = self.__registry.get(field_type, {}).get(lookup_name, None)

        if lookup_cls:
            return lookup_cls(field_value, lookup_value, case_sensitive)
        return None  # Lookup non trouvé


class Lookup(abc.ABC):
    lookup_name = None

    def __init__(self, db_value, value, sensitive=False):
        self.db_value = self.prepare_db_value(db_value)
        self.value = self.prepare_value(value)
        self.sensitive = sensitive
        self.prepare_lookup()
        if self.lookup_name is None
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


lookup_registry = _LookupRegistry()


class BuiltinLookup(Lookup):
    _op = None

    def as_bool(self):
        op = self._op or getattr(operator, self.lookup_name[1:] if self.sensitive else self.lookup_name, None)
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


class StrPrepareMixin(Lookup, abc.ABC):
    def prepare_db_value(self, db_value):
        if isinstance(db_value, str):
            return str(db_value).lower() if self.sensitive else str(db_value)
        return db_value

    def prepare_value(self, value):
        if isinstance(value, str):
            return str(value).lower() if self.sensitive else str(value)
        return value


@lookup_registry.register
class Exact(BuiltinLookup, StrPrepareMixin):
    _op = operator.eq
    lookup_name = 'exact'


@lookup_registry.register
class IExact(Exact):
    lookup_name = 'iexact'


class PrepareListValueMixin:

    def prepare_list_value(self):
        values = list(self.value)
        return values # TODO evaluate values

@lookup_registry.register
class In(BuiltinLookup, PrepareListValueMixin):
    lookup_name = 'in'
        
    @property
    def as_bool(self):
        return self.db_value in self.prepare_list_value()


@lookup_registry.register
class IsNull(BuiltinLookup):
    lookup_name = 'isnull'

    @property
    def  as_bool(self):
        if not isinstance(self.value, bool):
            raise ValueError('Value must be a boolean')
        return self.db_value is None if self.value else self.db_value is not None


class BuiltinStrLookup(Lookup):
    case_sensitive = True
    pass


@str_lookup
class StartsWith(BuiltinStrLookup):
    lookup_name = "startswith"

    def __call__(self, db_value, value, sensitive=False):
        return str(db_value).startswith(value) if sensitive else str(db_value).lower().startswith(value.lower())


@str_lookup
class EndsWith(BuiltinStrLookup):
    lookup_name = "endswith"

    def __call__(self, db_value, value, sensitive=False):
        return str(db_value).endswith(value) if sensitive else str(db_value).lower().endswith(value.lower())


@LookupRegistry.register(str, list, dict)
class Contains(BuiltinLookup):
    lookup_name = "contains"
    case_sensitive = True

    def __call__(self, db_value, value, sensitive=False):
        if isinstance(db_value, str) and isinstance(value, str) and sensitive:
            return value.lower() in db_value.lower()
        return value in db_value
