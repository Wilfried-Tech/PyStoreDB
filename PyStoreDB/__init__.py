from __future__ import annotations

import os
import threading

from PyStoreDB.conf import DEFAULT_STORE_NAME, PyStoreDBSettings
from PyStoreDB.core import CollectionReference, DocumentReference
from PyStoreDB.engines import PyStoreDBEngine
from PyStoreDB.errors import PyStoreDBNameError, PyStoreDBInitialisationError
from ._delegates import StoreDelegate

__all__ = ['PyStoreDB']
__version__ = '1.0.0'

from .constants import Json


class _PyStoreDBMeta(type):
    __instances: dict[str, PyStoreDB] = {}
    __lock = threading.Lock()
    __settings = PyStoreDBSettings()

    @property
    def settings(cls):
        return cls.__settings

    @settings.setter
    def settings(cls, setting: PyStoreDBSettings):
        cls.__settings = setting

    def __call__(cls, *args, **kwargs):
        raise ValueError(f"{cls.__name__} is not instantiable use get_instance instead")

    def close_instance(cls, name: str):
        return cls.__instances.pop(name)

    def clear_instances(cls):
        cls.__instances = {}

    def get_instance(cls, name: str = DEFAULT_STORE_NAME, *args, **kwargs) -> PyStoreDB:
        """
        Create or get an instance of PyStoreDB from name of store
        :param name: name of store
        """
        with cls.__lock:
            if name == '':
                name = DEFAULT_STORE_NAME
            if not cls.is_initialised:
                raise PyStoreDBInitialisationError('PyStoreDB is not initialized')
            if not name.isalnum():
                raise PyStoreDBNameError(name)
            if name not in cls.__instances:
                engine = cls.settings.engine_class(name)
                delegate = StoreDelegate(engine)
                instance = cls.__instances.setdefault(
                    name, super().__call__(name, delegate=delegate, *args, **kwargs)
                )
                cls._initialize_store(engine, instance)
            return cls.__instances[name]

    @staticmethod
    def _initialize_store(engine: PyStoreDBEngine, instance: PyStoreDB):
        setattr(engine, '_store', instance)
        engine.initialize()

    def initialize(cls) -> None:
        if cls.is_initialised:
            raise PyStoreDBInitialisationError
        if cls.settings.store_dir is not None:
            os.makedirs(cls.settings.store_dir, exist_ok=True)
        setattr(cls, '__initialised', True)

    @property
    def is_initialised(cls) -> bool:
        return hasattr(cls, '__initialised')


class PyStoreDB(metaclass=_PyStoreDBMeta):

    def __init__(self, name: str, delegate: StoreDelegate):
        self.name = name
        self._delegate = delegate

    def collection(self, path: str) -> CollectionReference[Json]:
        from ._impl import JsonCollectionReference
        return JsonCollectionReference(self._delegate.collection(path))

    def doc(self, path: str) -> DocumentReference[Json]:
        from ._impl import JsonDocumentReference
        return JsonDocumentReference(self._delegate.doc(path))

    def clear(self):
        self._delegate.engine.clear()

    def close(self):
        self.__class__.close_instance(self.name)

    def get_raw_data(self, path: str = '') -> dict:
        """
        Get raw data at path of store
        Args:
            path: path of an

        Returns:

        """
        return self._delegate.engine.get_raw(path)

    def __repr__(self):
        return f"<PyStoreDB name={self.name}>"
