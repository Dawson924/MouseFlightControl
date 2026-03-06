import yaml

from data.spec import FlatConfig


class ConfigData(FlatConfig):
    SPEC = {
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
            'freecam_toggle': {'type': bool, 'default': False},
        },
        'Window': {'width': {'type': int, 'min': 200, 'max': 800, 'default': 350}},
    }


def config_representer(dumper: yaml.Dumper, config: ConfigData) -> yaml.Node:
    return dumper.represent_mapping('tag:yaml.org,2002:map', config.to_dict())


def config_constructor(loader: yaml.Loader, node: yaml.Node) -> ConfigData:
    data = loader.construct_mapping(node, deep=False)
    return ConfigData.from_dict(data)


yaml.add_representer(ConfigData, config_representer)
yaml.add_constructor('!Config', config_constructor)
