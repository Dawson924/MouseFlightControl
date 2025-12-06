CONFIG_FILE = 'config.ini'
CONFIG = {
    'General': {
        'language': (str),
    },
    'Controls': {
        'mouse_speed': (int),
        'controller': (int),
        'key_toggle': (str),
        'key_center': (str),
        'key_freecam': (str),
        'key_view_center': (str),
        'camera_fov': (int),
        'key_taxi': (str),
    },
    'Options': {
        'show_cursor': (bool),
        'show_hint': (bool),
        'show_indicator': (bool),
        'button_mapping': (bool),
        'memorize_axis_pos': (bool),
        'freecam_auto_center': (bool),
    },
    'Window': {
        'w_size': (int),
    },
    'External': {},
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
