from typing import Any
from PyStoreDB.constants import supported_types

class PyStoreDBError(Exception):
    """Base class for all PyStoreDB exceptions."""
    def __init__(self, message: str = 'An Error Occur'):
        self.message = message
        super().__init__(self.message)

    def __repr__(self):
        return f"{self.__class__.__name__}(message='{self.message}')"

    def __str__(self):
        return self.message

class PyStoreDBInitialisationError(PyStoreDBError):
    """Exception raised when PyStoreDB is already initialized."""
    def __init__(self):
        super().__init__('PyStoreDB Already Initialised')

class PyStoreDBNameError(PyStoreDBError):
    """Exception raised for invalid store names."""
    def __init__(self, name: str):
        super().__init__(f'Name {name} is not alphanumeric')

class PyStoreDBPathError(PyStoreDBError):
    """Exception raised for invalid paths."""
    def __init__(self, path: str, segment: str = None):
        message = f'Invalid Path {path}'
        if segment:
            message += f' not found segment {segment}'
        super().__init__(message)

class PyStoreDBUnsupportedTypeError(PyStoreDBError):
    """Exception raised for unsupported types."""
    def __init__(self, value: Any):
        supported_types_list = ','.join([str(x) for x in supported_types])
        message = f'type {type(value).__name__} of value "{value}" is unsupported\nsupported types: {supported_types_list}'
        super().__init__(message)