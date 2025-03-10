from __future__ import annotations

import abc
from typing import Any

from PyStoreDB.constants import Json
from PyStoreDB.core import FieldPath

__all__ = ['PyStoreDBEngine']


class PyStoreDBEngine(abc.ABC):

    def __init__(self, store_name: str, **kwargs):
        """
        :type store PyStoreDBEngine
        """
        self.store_name = store_name

    @property
    def store(self):
        """
        Get the store object
        :rtype: PyStoreDB.PyStoreDB
        """
        return getattr(self, '_store', None)

    @property
    def in_memory(self):
        return self.store.__class__.settings.store_dir is None

    @abc.abstractmethod
    def path_exists(self, path: str) -> bool:
        pass

    @abc.abstractmethod
    def get_document(self, path: str) -> Json:
        pass

    @abc.abstractmethod
    def set(self, path: str, data: Json):
        pass

    @abc.abstractmethod
    def delete(self, path: str):
        pass

    @abc.abstractmethod
    def update(self, path: str, data: Json):
        pass

    @abc.abstractmethod
    def create_database_if_not_exists(self):
        pass

    def initialize(self):
        if not self.in_memory:
            self.create_database_if_not_exists()

    @abc.abstractmethod
    def get_field(self, path: str, field: str | FieldPath, default=None) -> Any:
        pass

    @abc.abstractmethod
    def save(self):
        pass

    @abc.abstractmethod
    def doc_exists(self, path) -> bool:
        pass

    @abc.abstractmethod
    def get_collection(self, path, **kwargs) -> dict[str, Json]:
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def get_raw(self, path):
        pass
