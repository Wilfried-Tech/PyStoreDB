from __future__ import annotations

import os
import threading

from PyStore.conf import DEFAULT_STORE_NAME, PyStoreSettings
from PyStore.core._json_collection import JsonCollectionReference
from PyStore.engines import PyStoreEngine
from PyStore.errors import PyStoreNameError, PyStoreInitialisationError
from ._delegates import StoreDelegate

__all__ = ['PyStore']

from PyStore.core._json_document import JsonDocumentReference


class _PyStoreMeta(type):
    __instances: dict[str, PyStore] = {}
    __lock = threading.Lock()
    __settings = PyStoreSettings()

    @property
    def settings(cls):
        return cls.__settings

    @settings.setter
    def settings(cls, setting: PyStoreSettings):
        cls.__settings = setting

    def __call__(cls, *args, **kwargs):
        raise ValueError(f"{cls.__name__} is not instantiable use get_instance instead")

    def destroy_instance(cls, name: str):
        return cls.__instances.pop(name)

    def clear_instances(cls):
        cls.__instances = {}

    def get_instance(cls, name: str = DEFAULT_STORE_NAME, *args, **kwargs) -> PyStore:
        """
        Create or get an instance of PyStore from name of store
        :param name: name of store
        """
        with cls.__lock:
            if name == '':
                name = DEFAULT_STORE_NAME
            if not cls.is_initialised:
                raise PyStoreInitialisationError('PyStore is not initialized')
            if not name.isalnum():
                raise PyStoreNameError(name)
            if name not in cls.__instances:
                engine = cls.settings.engine_class(name)
                delegate = StoreDelegate(engine)
                instance = cls.__instances.setdefault(
                    name, super().__call__(name, delegate=delegate, *args, **kwargs)
                )
                cls._initialize_store(engine, instance)
            return cls.__instances[name]

    @staticmethod
    def _initialize_store(engine: PyStoreEngine, instance: PyStore):
        setattr(engine, '_store', instance)
        engine.initialize()

    def initialize(cls) -> None:
        if cls.is_initialised:
            raise PyStoreInitialisationError
        if cls.settings.store_dir is not None:
            os.makedirs(cls.settings.store_dir, exist_ok=True)
        setattr(cls, '__initialised', True)

    @property
    def is_initialised(cls) -> bool:
        return hasattr(cls, '__initialised')


class PyStore(metaclass=_PyStoreMeta):

    def __init__(self, name: str, delegate: StoreDelegate):
        self.name = name
        self._delegate = delegate

    def collection(self, path: str) -> JsonCollectionReference:
        return JsonCollectionReference(self._delegate.collection(path))

    def doc(self, path: str) -> JsonDocumentReference:
        return JsonDocumentReference(self._delegate.doc(path))

    def clear(self):
        self._delegate.engine.clear()

    def destroy(self):
        self.__class__.destroy_instance(self.name)

    def get_raw_data(self, path: str = '') -> dict:
        return self._delegate.engine.get_raw(path)

    def __repr__(self):
        return f"<PyStore name={self.name}>"
