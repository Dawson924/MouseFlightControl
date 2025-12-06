import configparser
from os import path
from typing import Any, Dict

from common.config import CONFIGURABLE
from common.constants import SCRIPT_PATH
from lib.num import is_float, is_integer
from utils import similar


def load_config(file: str, namespace: str, default: Dict[str, Any]):
    if path.exists(file):
        parser = configparser.ConfigParser()
        parser.read(file, encoding='utf-8')
        if parser.has_section(namespace):
            config = {}
            for key, value in parser.items(namespace):
                if value.lower() == 'true':
                    config[key] = True
                elif value.lower() == 'false':
                    config[key] = False
                elif is_integer(value):
                    config[key] = int(value)
                elif is_float(value):
                    config[key] = float(value)
                else:
                    config[key] = value
            if similar(config, default):
                return config
        else:
            pass

    return default


def save_config(file: str, configs: Dict[str, Dict]) -> None:
    parser = configparser.ConfigParser()
    for section, data in configs.items():
        if not parser.has_section(section) and len(data) > 0:
            parser.add_section(section)
        for key, value in data.items():
            if isinstance(value, bool):
                str_val = str(value).lower()
            else:
                str_val = str(value)
            parser[section][key] = str_val
    with open(file, 'w', encoding='utf-8') as f:
        parser.write(f)


def validate_config(config: Dict[str, Any], silent: bool = False) -> Dict[str, Any]:
    """校验配置项的合法性（键名、类型、范围）"""
    _config = {}
    for key, value in config.items():
        if key not in CONFIGURABLE:
            if not silent:
                raise ValueError(
                    f"Invalid value: '{key}={value}' at {SCRIPT_PATH} ({key} does not exist)"
                )
            continue

        rule = CONFIGURABLE[key]
        expected_type = None
        is_tuple = False

        if isinstance(rule, tuple):
            expected_type = rule[0]
            is_tuple = True
        elif isinstance(rule, type):
            expected_type = rule

        if not isinstance(value, expected_type):
            if not silent:
                raise TypeError(
                    f'Invalid type: {type(value).__name__} at {SCRIPT_PATH}\n'
                    f'Use {expected_type.__name__} instead'
                )
            continue

        if is_tuple and len(rule) >= 3:
            min_val, max_val = rule[1], rule[2]
            valid = True
            if min_val is not None:
                valid &= value >= min_val
            if max_val is not None:
                valid &= value <= max_val
            if not valid:
                raise ValueError(
                    f"Invalid value: '{key}={value}' at {SCRIPT_PATH} (out of range: {min_val}~{max_val})"
                )

        _config[key] = value

    return _config
