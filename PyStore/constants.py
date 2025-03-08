import datetime
from typing import Union

NoneType = type(None)

standard_types = (int, float, bool, str, list, NoneType)

special_types = (dict, datetime.datetime)

supported_types = (*standard_types, *special_types)

Json = dict[str, Union[str, int, float, bool, list, NoneType, dict, datetime.datetime]]

LOOKUP_SEP = '__'
