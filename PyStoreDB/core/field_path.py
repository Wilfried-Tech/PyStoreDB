class _FieldPathMeta(type):
    """
    Metaclass for FieldPath to provide additional class-level properties.

    This metaclass adds a `document_id` property to the `FieldPath` class,
    which returns a special field path representing the document ID.
    """

    @property
    def document_id(cls):
        """
        Get the field path representing the document ID.

        Returns:
            FieldPath: A FieldPath instance representing the document ID.
        """
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
        """
        Initializes a FieldPath instance with the given field name.

        Args:
            field (str): The name of the field.
        """
        self.path = field
        # TODO implement nested fields to access map and list

    def __eq__(self, other):
        """
        Check if this FieldPath is equal to another FieldPath.

        Args:
            other (FieldPath): The other FieldPath to compare with.

        Returns:
            bool: True if both FieldPath instances have the same path, False otherwise.
        """
        return isinstance(other, FieldPath) and self.path == other.path

    def __hash__(self):
        """
        Get the hash value of the FieldPath.

        Returns:
            int: The hash value of the field path.
        """
        return hash(self.path)

    def __str__(self):
        """
        Get the string representation of the FieldPath.

        Returns:
            str: The string representation of the field path.
        """
        return self.path

    def __repr__(self):
        """
        Get the official string representation of the FieldPath.

        Returns:
            str: The official string representation of the field path.
        """
        return f'FieldPath({self.path})'

    def __get__(self, instance, owner):
        """
        Descriptor method to get the field path.

        Args:
            instance: The instance of the class where the descriptor is accessed.
            owner: The owner class of the descriptor.

        Returns:
            str: The field path.
        """
        return self.path

    def __set__(self, instance, value):
        """
        Descriptor method to set the field path, which is not allowed.

        Args:
            instance: The instance of the class where the descriptor is accessed.
            value: The value to set.

        Raises:
            AttributeError: Always raised since setting the field path is not allowed.
        """
        raise AttributeError('Cannot set FieldPath value')
