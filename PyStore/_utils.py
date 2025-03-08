from __future__ import annotations

from PyStore.constants import Json, supported_types
from PyStore.errors import PyStorePathError, PyStoreUnsupportedTypeError


def path_segments(path: str) -> list[str]:
    return path.strip('/').split('/')


def validate_path(path: str, partial=False) -> None:
    if not path:
        raise PyStorePathError(path, 'path "%s" cannot be empty')
    if not path.startswith('/') and not partial:
        raise PyStorePathError(path, 'path "%s" must start with /')
    if path.endswith('/'):
        raise PyStorePathError(path, 'path "%s" must not end with /')
    if '//' in path:
        raise PyStorePathError(path, 'path "%s" must not contain //')
    if not all([x.isalnum() for x in path.strip('/').split('/')]):
        raise PyStorePathError(path, 'path "%s" must be alphanumeric')


def is_valid_document(path: str, throw_error=True) -> bool:
    check = len(path.strip('/').split('/')) % 2 == 0
    if not check and throw_error:
        raise PyStorePathError(path, "'%s' doesn't point to a document")
    return check


def is_valid_collection(path: str, throw_error=True) -> bool:
    check = len(path.strip('/').split('/')) % 2 == 1
    if not check and throw_error:
        raise PyStorePathError(path, "'%s' doesn't point to a collection")
    return check


def parent_path(path: str) -> str | None:
    parent_segments = path.strip('/').split('/')[:-1]
    if len(parent_segments) == 0:
        return None
    return '/' + '/'.join(parent_segments)


def validate_data_value(value):
    if type(value) not in supported_types:
        raise PyStoreUnsupportedTypeError(value)
    if type(value) is list:
        for list_value in value:
            validate_data_value(list_value)
    elif type(value) is dict:
        validate_data(value)


def validate_data(data: Json):
    if not isinstance(data, dict):
        raise TypeError('data must be a dict')
    for key, value in data.items():
        if not isinstance(key, str):
            raise TypeError('data key must be str')
        validate_data_value(value)


def generate_uuid():
    import uuid
    # from datetime import datetime
    # return (str(datetime.now().timestamp()).replace('.', '') + uuid.uuid4().hex)[:20]
    return uuid.uuid4().hex[:20]
