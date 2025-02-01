import datetime
from typing import Union

standard_types = (int, float, bool, str, list)

special_types = (dict, datetime.datetime)

supported_types = (*standard_types, *special_types)

Json = dict[str, Union[str, int, float, bool, list, dict, datetime.datetime]]
