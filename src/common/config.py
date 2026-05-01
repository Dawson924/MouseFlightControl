CONFIG_FILE = 'config.yml'
FLIGHT_FILE = 'flight.yml'

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
