from typing import Any

from PyStoreDB.constants import supported_types


class PyStoreDBError(Exception):
    message = 'An Error Occur'

    def __init__(self, message: str | None = None):
        if message:
            self.message = str(message)
        super().__init__(self.message)

    def __repr__(self):
        return f"{self.__class__.__name__}(message='{self.message}')"

    def __str__(self):
        return self.message


class PyStoreDBInitialisationError(PyStoreDBError):
    message = 'PyStoreDB Already Initialised'


class PyStoreDBNameError(PyStoreDBError):
    message = 'Name %s is not alphanumeric'

    def __init__(self, name: str, message: str = None):
        self.name = name
        if message:
            self.message = message
        super().__init__(self.message % name)


class PyStoreDBPathError(PyStoreDBError):
    message = 'Invalid Path %s'
    message_with_segment = 'Invalid Path %s not found segment %s'

    def __init__(self, path: str, segment=None, message: str = None):
        self.path = path
        self.segment = segment
        if message:
            self.message = message
        if segment and message is None:
            super().__init__(self.message_with_segment % (path, segment))
        else:
            super().__init__(self.message % (path, segment))


class PyStoreDBUnsupportedTypeError(PyStoreDBError):
    supported_types_list = ','.join([str(x) for x in supported_types])
    message = f'type %s of value "%s" is unsupported\nsupported types:  ${supported_types_list}'

    def __init__(self, value: Any, message: str = None):
        self.type = type(value)
        if message:
            self.message = message
        super().__init__(self.message % (self.type.__name__, value))
