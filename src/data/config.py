import yaml

from data.store import HashStorage


class Config(HashStorage):
    SPEC = {
        'General': {'language': {'type': str, 'allowed': ['en_US', 'zh_CN', 'ru_RU'], 'default': 'en_US'}},
        'Controls': {
            'mouse_speed': {'type': int, 'min': 1, 'max': 20, 'default': 5, 'widget': 'Slider', 'i18n': 'Sensitive'},
            'key_toggle': {'type': str, 'default': '`', 'widget': 'KeybindEdit', 'i18n': 'ToggleEnabled'},
            'key_center': {'type': str, 'default': 'MMB', 'widget': 'KeybindEdit', 'i18n': 'CenterControl'},
            'key_freecam': {'type': str, 'default': 'tab', 'widget': 'KeybindEdit', 'i18n': 'EnableFreecam'},
            'key_view_center': {'type': str, 'default': 'capslock', 'widget': 'KeybindEdit', 'i18n': 'ViewCenter'},
            'key_taxi': {'type': str, 'default': 'alt + `', 'widget': 'KeybindEdit', 'i18n': 'TaxiMode'},
        },
        'Options': {
            'auto_connect': {'type': bool, 'default': False, 'widget': 'CheckBox', 'i18n': 'AutoConnect'},
            'show_cursor': {'type': bool, 'default': False, 'widget': 'CheckBox', 'i18n': 'ShowCursor'},
            'show_hint': {'type': bool, 'default': True, 'widget': 'CheckBox', 'i18n': 'HintOverlay'},
            'show_indicator': {'type': bool, 'default': False, 'widget': 'CheckBox', 'i18n': 'ShowIndicator'},
            'button_mapping': {'type': bool, 'default': True, 'widget': 'CheckBox', 'i18n': 'ButtonMapping'},
            'memorize_axis_pos': {'type': bool, 'default': True, 'widget': 'CheckBox', 'i18n': 'MemorizeAxisPos'},
            'freecam_auto_center': {'type': bool, 'default': False, 'widget': 'CheckBox', 'i18n': 'FreecamAutoCenter'},
            'freecam_toggle': {'type': bool, 'default': False, 'widget': 'CheckBox', 'i18n': 'FreecamToggle'},
        },
        'Window': {
            'width': {'type': int, 'default': 0},
            'height': {'type': int, 'default': 0},
        },
    }


def config_representer(dumper: yaml.Dumper, config: Config) -> yaml.Node:
    return dumper.represent_mapping('tag:yaml.org,2002:map', config.to_dict())


def config_constructor(loader: yaml.Loader, node: yaml.Node) -> Config:
    data = loader.construct_mapping(node, deep=False)
    return Config.from_dict(data)


yaml.add_representer(Config, config_representer)
yaml.add_constructor('!Config', config_constructor)
