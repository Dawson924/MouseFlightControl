import configparser
from os import path
from typing import Any, Dict

from utils import equal


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
                elif value.isdigit():
                    config[key] = int(value)
                else:
                    config[key] = value
            if equal(config, default):
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
