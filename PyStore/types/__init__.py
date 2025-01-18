import datetime

standard_types = (int, float, bool, str, list)

special_types = (dict, datetime.datetime)

supported_types = (*standard_types, *special_types)

Json = dict[str, str | int | float | bool | list | dict | datetime.datetime]
