CONFIG_FILE = 'config.yml'
INPUT_FILE = 'flight.yml'

CONFIG = {
    'General': {
        'language': 'string(min=1)',
        'flight_mode': 'integer(min=0)',
        'camera_fov': 'integer(min=1, max=180)',
    },
    'Controls': {
        'mouse_speed': 'integer(min=1, max=100)',
        'key_toggle': 'string(min=1)',
        'key_center': 'string(min=1)',
        'key_freecam': 'string(min=1)',
        'key_view_center': 'string(min=1)',
        'key_taxi': 'string(min=1)',
    },
    'Options': {
        'show_cursor': 'boolean',
        'show_hint': 'boolean',
        'show_indicator': 'boolean',
        'button_mapping': 'boolean',
        'memorize_axis_pos': 'boolean',
        'freecam_auto_center': 'boolean',
    },
    'Window': {
        'w_size': 'integer(min=100)',
    },
    'Flight': {},
}

CONFIGURABLE = {
    'target_fps': (int, 60, 500),
    'attempts': (int, 1, None),
    'debug': (bool),
    'indicator_x': (int),
    'indicator_y': (int),
    'indicator_bg_color': (list),
    'indicator_line_color': (list),
    'indicator_size': (int),
    'device': (str,),
    'device_id': (int, 1, None),
    'axis_speed': (int, 1, 20),
    'damping_h': (float, 0.01, 1),
    'damping_v': (float, 0.01, 1),
}

LANGUAGE_CONFIG = [
    {'code': 'en_US', 'display_name': 'English'},
    {'code': 'zh_CN', 'display_name': '简体中文'},
    {'code': 'ru_RU', 'display_name': 'Русский'},
]
