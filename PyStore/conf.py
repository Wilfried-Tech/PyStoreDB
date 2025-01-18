import os

from PyStore.engines import PyStoreEngine, PyStoreRawEngine

DEFAULT_STORE_NAME = 'default'


class PyStoreSettings:

    def __init__(self, store_dir: str = 'store', engine_class: PyStoreEngine = PyStoreRawEngine):
        self.store_dir = store_dir
        self.engine_class = engine_class

    @property
    def store_dir(self):
        return self.__store_dir

    @store_dir.setter
    def store_dir(self, path: str):
        if isinstance(path, str):
            self.__store_dir = os.path.abspath(path)

    @property
    def engine_class(self):
        return self.__engine_class

    @engine_class.setter
    def engine_class(self, kclass: type):
        if issubclass(kclass, PyStoreEngine):
            self.__engine_class = kclass
        else:
            raise TypeError(f"{kclass.__name__} is not subclass of PyStoreEngine")
