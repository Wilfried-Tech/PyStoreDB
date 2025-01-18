from typing import Any

from PyStore.types import supported_types


class PyStoreError(Exception):
    message = 'An Error Occur'

    def __init__(self, message: str | None = None):
        if message:
            self.message = str(message)
        super().__init__(self.message)

    def __repr__(self):
        return f"{self.__class__.__name__}(message='{self.message}')"

    def __str__(self):
        return self.message


class PyStoreInitialisationError(PyStoreError):
    message = 'PyStore Already Initialised'


class PyStoreNameError(PyStoreError):
    message = 'Name %s is not alphanumeric'

    def __init__(self, name: str, message: str = None):
        self.name = name
        if message:
            self.message = message
        super().__init__(self.message % name)


class PyStorePathError(PyStoreError):
    message = 'Invalid Path %s'

    def __init__(self, path: str, message: str = None):
        self.path = path
        if message:
            self.message = message
        super().__init__(self.message % path)


class PyStoreKeyError(PyStoreError):
    message = 'Key %s not found'

    def __init__(self, key: str, message: str = None):
        self.key = key
        if message:
            self.message = message
        super().__init__(self.message % key)


class PyStoreUnsupportedTypeError(PyStoreError):
    supported_types_list = ','.join([str(x) for x in supported_types])
    message = f'type %s of value "%s" is unsupported\nsupported types:  ${supported_types_list}'

    def __init__(self, value: Any, message: str = None):
        self.type = type(value)
        if message:
            self.message = message
        super().__init__(self.message % (self.type.__name__, value))
