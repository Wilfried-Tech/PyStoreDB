class _FieldPathMeta(type):

    @property
    def document_id(cls):
        return cls('__name__')


class FieldPath(metaclass=_FieldPathMeta):
    def __init__(self, field: str):
        self.field = field

    def __eq__(self, other):
        return isinstance(other, FieldPath) and self.field == other.field
