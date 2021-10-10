from __future__ import annotations

import logging
from functools import wraps
from pydoc import locate
from typing import Type

logger = logging.getLogger("z2t2ha.utils.decorators")


def require_argument(argument_name: str,
                     argument_type: Type | str = None):
    argument_type = locate(argument_type) if isinstance(argument_type, str) else argument_type

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if (argument_value := kwargs.get(argument_name, None)) is None:
                logger.debug("not running %s, argument %s is not present", argument_name)
                return

            if argument_type is not None and not isinstance(argument_value, argument_type):
                logger.debug("not running %s, argument %s is not %s (actual type is %s)",
                             function, argument_name, argument_type, type(argument_value))
                return

            return function(*args, **kwargs)
        return wrapper
    return decorator


def require_dict_argument_property(property_path: str,
                                   property_type: Type | str = None,
                                   argument_name: str = "payload"):
    property_type = locate(property_type) if isinstance(property_type, str) else property_type

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if (payload := kwargs.get(argument_name, None)) is None:
                logger.debug("not running %s, argument %s is not present",  function, argument_name)
                return

            if not isinstance(payload, dict):
                logger.debug("not running %s, argument %s is not dict (actual type is %s)",
                             function, argument_name, type(payload))
                return

            partial_property_path = property_path
            property_value = payload
            _undefined = "_undefined"
            while partial_property_path and property_value is not _undefined:
                property_name, _, partial_property_path = partial_property_path.partition(".")
                property_value = property_value.get(property_name, _undefined)

            if property_value is _undefined:
                logger.debug("not running %s, property '%s' of dict argument %s is not present",
                             function, property_path, argument_name)
                return

            if property_type is not None and not isinstance(property_value, property_type):
                logger.debug("not running %s, property '%s' of dict argument %s is not %s (actual type is %s)",
                             function, property_path, argument_name, property_type, type(property_value))
                return

            return function(*args, **kwargs)
        return wrapper
    return decorator
