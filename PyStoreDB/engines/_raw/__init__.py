from __future__ import annotations

import os.path
from typing import Any

from PyStoreDB._utils import validate_data, validate_path, is_valid_document, is_valid_collection
from PyStoreDB.constants import Json
from PyStoreDB.core import FieldPath
from PyStoreDB.engines._raw import utils, query
from PyStoreDB.engines.base import PyStoreDBEngine
from PyStoreDB.errors import PyStoreDBPathError

__all__ = ['PyStoreDBRawEngine']


class PyStoreDBRawEngine(PyStoreDBEngine):

    def __init__(self, store_name: str, **kwargs):
        super().__init__(store_name, **kwargs)
        self._save_file = None
        self._raw_db = {}
        self.query_engine = query.PyStoreDBRawQuery()

    def create_database_if_not_exists(self):
        utils.create_database(self._save_file)

    def initialize(self):
        if not self.in_memory:
            self._save_file = os.path.join(self.store.__class__.settings.store_dir, f'{self.store_name}.json')
            super().initialize()
            self._raw_db = utils.load_db(self._save_file)

    def delete(self, path: str):
        utils.delete_document(path, self._raw_db)
        self.save()

    def get_document(self, path: str) -> Json:
        data = utils.get_nested_doc_dict(path, self._raw_db)
        return utils.decode_document_data(data)

    def get_collection(self, path: str, **kwargs) -> dict[str, Json]:
        try:
            data = utils.get_nested_dict(path, self._raw_db)
            data = utils.decode_collection_docs(data)
            return self.query_engine.apply_query_filters(data, **kwargs)
        except PyStoreDBPathError:
            return {}

    def get_raw(self, path: str):
        if path == '':
            return utils.decode_all_data(self._raw_db)
        validate_path(path)
        if is_valid_collection(path, throw_error=False) or is_valid_document(path, throw_error=False):
            return utils.decode_all_data(utils.get_nested_dict(path, self._raw_db))
        else:
            raise PyStoreDBPathError(f'Invalid path: {path}\nThis path doesn\'t point at a document or collection')

    def set(self, path: str, data: Json):
        validate_data(data)
        item = utils.create_nested_dict(path, self._raw_db)
        item.clear()
        item.update(utils.encode_data(data))
        self.save()

    def update(self, path: str, data: Json):
        validate_data(data)
        item = utils.get_nested_doc_dict(path, self._raw_db)
        utils.update_data(item, data)
        self.save()

    def path_exists(self, path: str) -> bool:
        try:
            utils.get_nested_dict(path, self._raw_db)
            return True
        except PyStoreDBPathError:
            return False

    def doc_exists(self, path):
        try:
            data = utils.get_nested_doc_dict(path, self._raw_db)
            if utils.DATA_KEY in data:
                return True
            return False
        except PyStoreDBPathError:
            return False

    def get_field(self, path: str, field: str | FieldPath, default=None) -> Any:
        if field == FieldPath.document_id:
            return path.split('/')[-1]
        return self.get_document(path).get(field if isinstance(field, str) else field.path, default)

    def clear(self):
        self._raw_db = {}
        self.save()

    def save(self):
        if not self.in_memory:
            utils.save_database(self._save_file, self._raw_db)
