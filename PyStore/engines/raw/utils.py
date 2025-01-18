import json
import os
from datetime import datetime
from typing import Any

from PyStore._utils import path_segments
from PyStore.errors import PyStoreKeyError
from PyStore.types import Json, supported_types

"""""
{
    collection: {
        "adskafwekdk...": {
            sub_collection: {...}
            ...
            __data__:{
                a: 1,
                ...,
                custom: {
                    __meta__:{
                        type: time
                    }
                    value: '23:56'
                }
            }
        }
    }
}
"""""

DATA_KEY = '__data__'
META_KEY = '__meta__'
META_TYPE_KEY = 'type'
META_TYPE_VALUE_KEY = 'value'
DICT_META_KEY = 'dict'
DATETIME_META_KEY = 'datetime'


def create_database(path: str):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(json.dumps({}, indent=4))


def save_database(path: str, data: Json):
    # TODO encrypt
    if os.path.exists(path):
        with open(path, 'w') as f:
            f.write(json.dumps(data, indent=4))


def create_nested_dict(path: str, data: dict):
    if not path:
        return data
    keys = path_segments(path)
    for i, key in enumerate(keys):
        data = data.setdefault(key, {})
    return data


def get_nested_dict(path: str, data: dict):
    if not path:
        return data
    keys = path_segments(path)
    for key in keys:
        if key not in data:
            raise PyStoreKeyError(key)
        data = data[key]
    return data


def load_db(path: str) -> Json:
    with open(path) as f:
        data = json.load(f)
    return data


def parse_value_metadata(value) -> Any:
    if not isinstance(value, supported_types):
        raise ValueError(f'{value} is not supported')
    elif isinstance(value, dict):
        if META_KEY not in value:
            raise ValueError
        meta = value[META_KEY]
        if meta[META_TYPE_KEY] == DICT_META_KEY:
            return value[META_TYPE_VALUE_KEY]
        if meta[META_TYPE_KEY] == DATETIME_META_KEY:
            return datetime.fromisoformat(value[META_TYPE_VALUE_KEY])
    return value


def encode_value_metadata(value) -> Any:
    if isinstance(value, dict):
        return {
            META_KEY: {
                META_TYPE_KEY: DICT_META_KEY,
                META_TYPE_VALUE_KEY: value
            }
        }
    if isinstance(value, datetime):
        return {
            META_KEY: {
                META_TYPE_KEY: DATETIME_META_KEY,
                META_TYPE_VALUE_KEY: datetime.isoformat(value)
            }
        }
    return value


def encode_data(data: Json):
    encoded = {DATA_KEY: {}}
    for key, value in data.items():
        encoded[DATA_KEY][key] = encode_value_metadata(value)
    return encoded


def update_data(data: Json, new_data: Json):
    for key, value in new_data.items():
        data[DATA_KEY][key] = encode_value_metadata(value)
    return data


def decode_document_data(data: Json) -> Json:
    _data = {}
    for key, value in data[DATA_KEY].items():
        _data[key] = parse_value_metadata(value)
    return _data


def delete_document(path: str, data: Json):
    *paths, _id = path_segments(path)
    for key in paths:
        if key not in data:
            raise PyStoreKeyError(key)
        data = data[key]
    if _id not in data:
        raise PyStoreKeyError(_id)
    elif DATA_KEY in data[_id]:
        del data[_id][DATA_KEY]


def decode_collection_docs(data):
    decoded = {}
    for key, value in data.items():
        decoded[key] = decode_document_data(value)
    return decoded
