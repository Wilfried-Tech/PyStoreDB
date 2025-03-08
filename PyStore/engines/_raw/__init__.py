from __future__ import annotations

import os.path
from typing import Any

from PyStore._utils import validate_data
from PyStore.constants import Json
from PyStore.core import FieldPath
from PyStore.engines._raw import utils, query
from PyStore.engines.base import PyStoreEngine
from PyStore.errors import PyStorePathError

__all__ = ['PyStoreRawEngine']


class PyStoreRawEngine(PyStoreEngine):

    def __init__(self, store_name: str, **kwargs):
        super().__init__(store_name, **kwargs)
        self._save_file = None
        self._raw_db = {}
        self.query_engine = query.PyStoreRawQuery()

    def create_database_if_not_exists(self):
        utils.create_database(self._save_file)

    def initialize(self):
        if not self.in_memory:
            self._save_file = os.path.join(self.store.__class__.settings.store_dir, f'{self.store_name}.json')
            super().initialize()
            self._raw_db = utils.load_db(self._save_file)

    def delete(self, path: str):
        return utils.delete_document(path, self._raw_db)

    def get_document(self, path: str) -> Json:
        data = utils.get_nested_doc_dict(path, self._raw_db)
        return utils.decode_document_data(data)

    def get_collection(self, path: str, **kwargs) -> dict[str, Json]:
        try:
            data = utils.get_nested_dict(path, self._raw_db)
            data = utils.decode_collection_docs(data)
            return self.query_engine.apply_query_filters(data, **kwargs)
        except PyStorePathError:
            return {}

    def get_raw(self, path: str):
        if path == '':
            return utils.decode_all_data(self._raw_db)
        return utils.decode_all_data(utils.get_nested_dict(path, self._raw_db))

    def set(self, path: str, data: Json):
        validate_data(data)
        item = utils.create_nested_dict(path, self._raw_db)
        item.clear()
        item.update(utils.encode_data(data))

    def update(self, path: str, data: Json):
        validate_data(data)
        item = utils.get_nested_doc_dict(path, self._raw_db)
        utils.update_data(item, data)

    def path_exists(self, path: str) -> bool:
        try:
            utils.get_nested_dict(path, self._raw_db)
            return True
        except PyStorePathError:
            return False

    def doc_exists(self, path):
        try:
            data = utils.get_nested_doc_dict(path, self._raw_db)
            if utils.DATA_KEY in data:
                return True
            return False
        except PyStorePathError:
            return False

    def get_field(self, path: str, field: str | FieldPath, default=None) -> Any:
        if field == FieldPath.document_id:
            return path.split('/')[-1]
        return self.get_document(path).get(field if isinstance(field, str) else field.path, default)

    def clear(self):
        self._raw_db = {}

    def save(self):
        utils.save_database(self._save_file, self._raw_db)
