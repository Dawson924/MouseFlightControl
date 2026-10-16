import yaml

from common.axis import CONTROL_AXES, JOYSTICK_AXES, ControlAxis
from connect.platform import Simulator
from data import YamlStorage
from type.filter import Filter, Filters


class FlightData(YamlStorage):
    SPEC = {
        'Connect': {
            'model': {'type': str, 'default': ''},
            'simulator': {'type': str, 'default': Simulator.DCS},
        },
        'Input': {
            'flight_mode': {
                'type': int,
                'allowed': [-1, 0, 1, 2, 3],
                'default': 0,
            },  # -1 has no definition. The only reason to use it is to avoid errors from spec validation.
            'camera_fov': {
                'type': int,
                'min': 40,
                'max': 160,
                'default': 100,
                'widget': 'SpinBox',
                'i18n': 'CameraFov',
            },
            'thrust_speed': {
                'type': int,
                'min': 100,
                'max': 1000,
                'default': 500,
                'widget': 'SpinBox',
                'i18n': 'ThrustSpeed',
            },
            'rudder_speed': {
                'type': int,
                'min': 100,
                'max': 1000,
                'default': 120,
                'widget': 'SpinBox',
                'i18n': 'RudderSpeed',
            },
            'throttle_increase': {'type': str, 'default': 'X', 'widget': 'KeybindEdit', 'i18n': 'ThrustIncrease'},
            'throttle_decrease': {'type': str, 'default': 'Z', 'widget': 'KeybindEdit', 'i18n': 'ThrustDecrease'},
            'collective_increase': {'type': str, 'default': 'W', 'widget': 'KeybindEdit', 'i18n': 'ThrustIncrease'},
            'collective_decrease': {'type': str, 'default': 'S', 'widget': 'KeybindEdit', 'i18n': 'ThrustDecrease'},
            'collective_maximum': {'type': str, 'default': '', 'widget': 'KeybindEdit', 'i18n': 'CollectiveMaximum'},
            'collective_minimum': {'type': str, 'default': 'Z', 'widget': 'KeybindEdit', 'i18n': 'CollectiveMinimum'},
            'rudder_left': {'type': str, 'default': 'A', 'widget': 'KeybindEdit', 'i18n': 'RudderLeft'},
            'rudder_right': {'type': str, 'default': 'D', 'widget': 'KeybindEdit', 'i18n': 'RudderRight'},
            'rudder_center': {'type': str, 'default': 'X', 'widget': 'KeybindEdit', 'i18n': 'RudderCenter'},
        },
        'Joystick': {
            axis: {
                'type': dict,
                'default': {
                    'axis': JOYSTICK_AXES[i],
                    'invert': axis in ['Throttle', 'ZoomView'],
                    'curvature': 0.0,
                    'deadzone': 0.0,
                },
                'fields': {
                    'axis': {'type': str},
                    'invert': {'type': bool},
                    'curvature': {'type': float, 'min': -1.0, 'max': 1.0},
                    'deadzone': {'type': float, 'min': 0.0, 'max': 1.0},
                },
            }
            for i, axis in enumerate(CONTROL_AXES)
        },
    }
    DEFAULT_GROUP = 'Input'

    def has(self, field: str) -> bool:
        return field in self.SPEC[self.DEFAULT_GROUP]

    def get_filters(self) -> Filters:
        return {k: Filter.from_dict(v) for k, v in self._data['Joystick'].items()}

    def get_filter(self, axis: ControlAxis) -> Filter:
        return Filter.from_dict(self._data['Joystick'][axis])

    def set_filter(self, axis: ControlAxis, filter: Filter) -> None:
        self._data['Joystick'][axis] = filter.to_dict()


def flight_config_representer(dumper: yaml.Dumper, config: FlightData) -> yaml.Node:
    return dumper.represent_mapping('tag:yaml.org,2002:map', config.to_dict())


def flight_config_constructor(loader: yaml.Loader, node: yaml.Node) -> FlightData:
    data = loader.construct_mapping(node, deep=True)
    return FlightData.from_dict(data)


yaml.add_representer(FlightData, flight_config_representer)
yaml.add_constructor('!FlightConfig', flight_config_constructor)
