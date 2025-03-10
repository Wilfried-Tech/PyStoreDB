import os

from PyStoreDB.engines import PyStoreDBEngine, PyStoreDBRawEngine

DEFAULT_STORE_NAME = 'default'

__all__ = ['PyStoreDBSettings', 'DEFAULT_STORE_NAME']


class PyStoreDBSettings:

    def __init__(self, store_dir: str = 'store', engine_class: PyStoreDBEngine = PyStoreDBRawEngine):
        self.store_dir = store_dir
        self.engine_class = engine_class

    @property
    def store_dir(self):
        return self.__store_dir

    @store_dir.setter
    def store_dir(self, path: str):
        if isinstance(path, str):
            self.__store_dir = None if path == ':memory:' else os.path.abspath(path)

    @property
    def engine_class(self):
        return PyStoreDBRawEngine if self.store_dir is None else self.__engine_class

    @engine_class.setter
    def engine_class(self, kclass: type):
        if issubclass(kclass, PyStoreDBEngine):
            self.__engine_class = kclass
        else:
            raise TypeError(f"{kclass.__name__} is not subclass of PyStoreDBEngine")
