class _FieldPathMeta(type):

    @property
    def document_id(cls):
        return cls('__name__')


class FieldPath(metaclass=_FieldPathMeta):
    """
    Represents a field path in a structured object.

    This class encapsulates the concept of a field path, which serves as
    an identifier for a specific field in a data structure. The `FieldPath`
    class is immutable and is primarily intended to provide easy access and
    manipulation of field paths in objects. It provides methods for equality
    comparison, hashing, and string representations for use in various
    contexts.

    Attributes:
        path (str): The string representation of the field path.
    """
    def __init__(self, field: str):
        self.path = field
        # TODO implement nested fields to access map an list

    def __eq__(self, other):
        return isinstance(other, FieldPath) and self.path == other.path

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return self.path

    def __repr__(self):
        return f'FieldPath({self.path})'

    def __get__(self, instance, owner):
        return self.path

    def __set__(self, instance, value):
        raise AttributeError('Cannot set FieldPath value')
