import os

from PyStoreDB.engines import PyStoreDBEngine, PyStoreDBRawEngine

DEFAULT_STORE_NAME = 'default'

__all__ = ['PyStoreDBSettings', 'DEFAULT_STORE_NAME']


class PyStoreDBSettings:
    """Configuration class for PyStoreDB.

    Attributes:
        store_dir (str): The directory for storage.
        engine_class (type): The engine class to use.
    """

    def __init__(self, store_dir: str = 'store', engine_class: PyStoreDBEngine = PyStoreDBRawEngine):
        """Initializes the PyStoreDB settings.

        Args:
            store_dir (str): The directory for storage.
            engine_class (type): The engine class to use.
        """
        self.store_dir = store_dir
        self.engine_class = engine_class

    @property
    def store_dir(self):
        """Gets the storage directory.

        Returns:
            str: The storage directory.
        """
        return self.__store_dir

    @store_dir.setter
    def store_dir(self, path: str):
        """Sets the storage directory.

        Args:
            path (str): The path to the storage directory.
        """
        if isinstance(path, str):
            self.__store_dir = None if path == ':memory:' else os.path.abspath(path)

    @property
    def engine_class(self):
        """Gets the engine class.

        Returns:
            type: The engine class.
        """
        return PyStoreDBRawEngine if self.store_dir is None else self.__engine_class

    @engine_class.setter
    def engine_class(self, kclass: type):
        """Sets the engine class.

        Args:
            kclass (type): The engine class.

        Raises:
            TypeError: If the class is not a subclass of PyStoreDBEngine.
        """
        if issubclass(kclass, PyStoreDBEngine):
            self.__engine_class = kclass
        else:
            raise TypeError(f"{kclass.__name__} is not subclass of PyStoreDBEngine")