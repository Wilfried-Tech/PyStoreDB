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
    """Metaclass for PyStoreDB to manage singleton instances and initialization."""

    __instances: dict[str, PyStoreDB] = {}
    __lock = threading.Lock()
    __settings = PyStoreDBSettings()

    @property
    def settings(cls):
        """Get the current settings for PyStoreDB.

        Returns:
            PyStoreDBSettings: The current settings.
        """
        return cls.__settings

    @settings.setter
    def settings(cls, setting: PyStoreDBSettings):
        """Set the settings for PyStoreDB.

        Args:
            setting (PyStoreDBSettings): The new settings.
        """
        cls.__settings = setting

    def __call__(cls, *args, **kwargs):
        """Prevent direct instantiation of PyStoreDB.

        Raises:
            ValueError: If an attempt is made to instantiate PyStoreDB directly.
        """
        raise ValueError(f"{cls.__name__} is not instantiable use get_instance instead")

    def close_instance(cls, name: str):
        """Close and remove an instance of PyStoreDB by name.

        Args:
            name (str): The name of the instance to close.

        Returns:
            PyStoreDB: The removed instance.
        """
        return cls.__instances.pop(name)

    def clear_instances(cls):
        """Clear all instances of PyStoreDB."""
        cls.__instances = {}

    def get_instance(cls, name: str = DEFAULT_STORE_NAME, *args, **kwargs) -> PyStoreDB:
        """Create or get an instance of PyStoreDB by name.

        Args:
            name (str): Name of the store.

        Returns:
            PyStoreDB: Instance of PyStoreDB.

        Raises:
            PyStoreDBInitialisationError: If PyStoreDB is not initialized.
            PyStoreDBNameError: If the store name is invalid.
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
        """Initialize the store with the given engine and instance.

        Args:
            engine (PyStoreDBEngine): The engine to use.
            instance (PyStoreDB): The instance to initialize.
        """
        setattr(engine, '_store', instance)
        engine.initialize()

    def initialize(cls) -> None:
        """Initialize PyStoreDB.

        Raises:
            PyStoreDBInitialisationError: If PyStoreDB is already initialized.
        """
        if cls.is_initialised:
            raise PyStoreDBInitialisationError
        if cls.settings.store_dir is not None:
            os.makedirs(cls.settings.store_dir, exist_ok=True)
        setattr(cls, '__initialised', True)

    @property
    def is_initialised(cls) -> bool:
        """Check if PyStoreDB is initialized.

        Returns:
            bool: True if initialized, False otherwise.
        """
        return hasattr(cls, '__initialised')


class PyStoreDB(metaclass=_PyStoreDBMeta):
    """Main class for PyStoreDB, representing a database store."""

    def __init__(self, name: str, delegate: StoreDelegate):
        """Initialize a PyStoreDB instance.

        Args:
            name (str): Name of the store.
            delegate (StoreDelegate): Store delegate for handling operations.
        """
        self.name = name
        self._delegate = delegate

    def collection(self, path: str) -> CollectionReference[Json]:
        """Get a collection reference by path.

        Args:
            path (str): Path to the collection.

        Returns:
            CollectionReference[Json]: CollectionReference object.
        """
        from ._impl import JsonCollectionReference
        return JsonCollectionReference(self._delegate.collection(path))

    def doc(self, path: str) -> DocumentReference[Json]:
        """Get a document reference by path.

        Args:
            path (str): Path to the document.

        Returns:
            DocumentReference[Json]: DocumentReference object.
        """
        from ._impl import JsonDocumentReference
        return JsonDocumentReference(self._delegate.doc(path))

    def clear(self):
        """Clear the store."""
        self._delegate.engine.clear()

    def close(self):
        """Close the store instance."""
        self.__class__.close_instance(self.name)

    def get_raw_data(self, path: str = '') -> dict:
        """Get raw data at the specified path of the store.

        Args:
            path (str): Path within the store.

        Returns:
            dict: Raw data as a dictionary.
        """
        return self._delegate.engine.get_raw(path)

    def __repr__(self):
        """Return a string representation of the PyStoreDB instance.

        Returns:
            str: String representation of the instance.
        """
        return f"<PyStoreDB name={self.name}>"
