from typing import Any, Dict

import yaml

CONFIG_META: Dict[str, Dict[str, Any]] = {
    'General': {'language': {'type': str, 'allowed': ['en_US', 'zh_CN', 'ru_RU'], 'default': 'en_US'}},
    'Controls': {
        'mouse_speed': {'type': int, 'min': 1, 'max': 20, 'default': 5},
        'key_toggle': {'type': str, 'default': '`'},
        'key_center': {'type': str, 'default': 'MMB'},
        'key_freecam': {'type': str, 'default': 'tab'},
        'key_view_center': {'type': str, 'default': 'capslock'},
        'key_taxi': {'type': str, 'default': 'alt + `'},
    },
    'Options': {
        'show_cursor': {'type': bool, 'default': False},
        'show_hint': {'type': bool, 'default': True},
        'show_indicator': {'type': bool, 'default': False},
        'button_mapping': {'type': bool, 'default': True},
        'memorize_axis_pos': {'type': bool, 'default': True},
        'freecam_auto_center': {'type': bool, 'default': False},
    },
    'Window': {'w_size': {'type': int, 'min': 200, 'max': 800, 'default': 350}},
}

SPECS = {}
for group in CONFIG_META.values():
    SPECS.update(group)
FIELDS = list(SPECS.keys())


class Config:
    def __init__(self):
        for field in FIELDS:
            setattr(self, field, SPECS[field]['default'])

    def _validate_value(self, key: str, value: Any):
        if key not in SPECS:
            raise ValueError(f'Invalid config key: {key}')

        spec = SPECS[key]
        if not isinstance(value, spec['type']):
            raise TypeError(f'{key} must be {spec["type"].__name__}, got {type(value).__name__}')

        if 'min' in spec and value < spec['min']:
            raise ValueError(f'{key} must be >= {spec["min"]} (got {value})')
        if 'max' in spec and value > spec['max']:
            raise ValueError(f'{key} must be <= {spec["max"]} (got {value})')

        if 'allowed' in spec and value not in spec['allowed']:
            raise ValueError(f'{key} must be one of {spec["allowed"]} (got {value})')

    def to_dict(self) -> dict:
        data = {}
        for group, fields in CONFIG_META.items():
            data[group] = {field: getattr(self, field) for field in fields.keys()}
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        config = cls()
        for group, fields in CONFIG_META.items():
            if group in data and isinstance(data[group], dict):
                for field in fields.keys():
                    if field in data[group]:
                        config.set(field, data[group][field])
        return config

    @classmethod
    def from_yaml(cls, yaml_str: str = None, file_path: str = None) -> 'Config':
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
        elif yaml_str:
            raw_data = yaml.safe_load(yaml_str)
        else:
            raise ValueError()

        if isinstance(raw_data, Config):
            return raw_data
        return cls.from_dict(raw_data)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            self.set(key, value)

    def set(self, key: str, value: Any):
        if key in SPECS:
            super().__setattr__(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        if key in SPECS:
            return getattr(self, key, default)
        return default


def config_representer(dumper: yaml.Dumper, config: Config) -> yaml.Node:
    return dumper.represent_mapping('tag:yaml.org,2002:map', config.to_dict())


def config_constructor(loader: yaml.Loader, node: yaml.Node) -> Config:
    data = loader.construct_mapping(node, deep=False)
    return Config.from_dict(data)


yaml.add_representer(Config, config_representer)
yaml.add_constructor('!Config', config_constructor)
