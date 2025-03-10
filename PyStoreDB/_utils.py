from __future__ import annotations

from PyStoreDB.constants import Json, supported_types
from PyStoreDB.errors import PyStoreDBPathError, PyStoreDBUnsupportedTypeError


def path_segments(path: str) -> list[str]:
    """Splits a path into its segments.

    Args:
        path (str): The path to split.

    Returns:
        list[str]: A list of path segments.
    """
    return path.strip('/').split('/')


def validate_path(path: str, partial=False) -> None:
    """Validates a given path.

    Args:
        path (str): The path to validate.
        partial (bool, optional): Whether the path is partial. Defaults to False.

    Raises:
        PyStoreDBPathError: If the path is invalid.
    """
    if not path:
        raise PyStoreDBPathError(path, 'path "%s" cannot be empty')
    if not path.startswith('/') and not partial:
        raise PyStoreDBPathError(path, 'path "%s" must start with /')
    if path.endswith('/'):
        raise PyStoreDBPathError(path, 'path "%s" must not end with /')
    if '//' in path:
        raise PyStoreDBPathError(path, 'path "%s" must not contain //')
    if not all([x.isalnum() for x in path.strip('/').split('/')]):
        raise PyStoreDBPathError(path, 'path "%s" must be alphanumeric')


def is_valid_document(path: str, throw_error=True) -> bool:
    """Checks if a path points to a valid document.

    Args:
        path (str): The path to check.
        throw_error (bool, optional): Whether to throw an error if the path is invalid. Defaults to True.

    Returns:
        bool: True if the path points to a valid document, False otherwise.

    Raises:
        PyStoreDBPathError: If the path is invalid and throw_error is True.
    """
    check = len(path.strip('/').split('/')) % 2 == 0
    if not check and throw_error:
        raise PyStoreDBPathError(path, "'%s' doesn't point to a document")
    return check


def is_valid_collection(path: str, throw_error=True) -> bool:
    """Checks if a path points to a valid collection.

    Args:
        path (str): The path to check.
        throw_error (bool, optional): Whether to throw an error if the path is invalid. Defaults to True.

    Returns:
        bool: True if the path points to a valid collection, False otherwise.

    Raises:
        PyStoreDBPathError: If the path is invalid and throw_error is True.
    """
    check = len(path.strip('/').split('/')) % 2 == 1
    if not check and throw_error:
        raise PyStoreDBPathError(path, "'%s' doesn't point to a collection")
    return check


def parent_path(path: str) -> str | None:
    """Gets the parent path of a given path.

    Args:
        path (str): The path to get the parent of.

    Returns:
        str | None: The parent path, or None if there is no parent.
    """
    parent_segments = path.strip('/').split('/')[:-1]
    if len(parent_segments) == 0:
        return None
    return '/' + '/'.join(parent_segments)


def validate_data_value(value):
    """Validates a data value.

    Args:
        value: The value to validate.

    Raises:
        PyStoreDBUnsupportedTypeError: If the value type is unsupported.
    """
    if type(value) not in supported_types:
        raise PyStoreDBUnsupportedTypeError(value)
    if type(value) is list:
        for list_value in value:
            validate_data_value(list_value)
    elif type(value) is dict:
        validate_data(value)


def validate_data(data: Json):
    """Validates a data dictionary.

    Args:
        data (Json): The data dictionary to validate.

    Raises:
        TypeError: If the data is not a dictionary or contains invalid keys or values.
    """
    if not isinstance(data, dict):
        raise TypeError('data must be a dict')
    for key, value in data.items():
        if not isinstance(key, str):
            raise TypeError('data key must be str')
        validate_data_value(value)


def generate_uuid():
    """Generates a UUID.

    Returns:
        str: A 20-character UUID.
    """
    import uuid
    # from datetime import datetime
    # return (str(datetime.now().timestamp()).replace('.', '') + uuid.uuid4().hex)[:20]
    return uuid.uuid4().hex[:20]
