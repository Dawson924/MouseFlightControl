from typing import Any, Dict

import yaml

from common.axis import AxisName
from data.spec import Config
from type.filter import Filter

AXIS_NAMES = ['x', 'y', 'z', 'rx', 'ry', 'rz', 'sl', 'sl2']


class FlightData(Config):
    SPEC = {
        'Connect': {
            'model': {'type': str, 'default': ''},
        },
        'Input': {
            'flight_mode': {'type': int, 'allowed': [-1, 0, 1, 2], 'default': 0},
            'camera_fov': {'type': int, 'min': 60, 'max': 160, 'default': 100},
            'throttle_speed': {'type': int, 'min': 100, 'max': 1000, 'default': 500},
            'collective_speed': {'type': int, 'min': 100, 'max': 1000, 'default': 140},
            'pedals_speed': {'type': int, 'min': 100, 'max': 1000, 'default': 120},
            'throttle_increase': {'type': str, 'default': 'x'},
            'throttle_decrease': {'type': str, 'default': 'z'},
        },
        'Axis': {
            axis_name: {
                'type': dict,
                'default': {
                    'invert': axis_name in ['z', 'sl'],
                    'curvature': 0.0,
                    'deadzone': 0.0,
                },
                'fields': {
                    'invert': {'type': bool},
                    'curvature': {'type': float, 'min': -1.0, 'max': 1.0},
                    'deadzone': {'type': float, 'min': 0.0, 'max': 1.0},
                },
            }
            for axis_name in AXIS_NAMES
        },
    }
    DEFAULT_GROUP = 'Input'

    def has(self, field: str) -> bool:
        return field in self.SPEC[self.DEFAULT_GROUP]

    def set(self, field: str, value: Any) -> None:
        self._set(self.DEFAULT_GROUP, field, value)

    def get(self, field: str, default: Any = None) -> Any:
        return self._get(self.DEFAULT_GROUP, field, default)

    def get_filters(self) -> Dict[str, Filter]:
        return {k: Filter.from_dict(v) for k, v in self._data['Axis'].items()}

    def get_filter(self, axis_id: AxisName) -> Filter:
        return Filter.from_dict(self._data['Axis'][axis_id])

    def set_filter(self, axis_id: AxisName, filter: Filter) -> None:
        self._data['Axis'][axis_id] = filter.to_dict()

    def __getitem__(self, key: str) -> Any:
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value


def flight_config_representer(dumper: yaml.Dumper, config: FlightData) -> yaml.Node:
    return dumper.represent_mapping('tag:yaml.org,2002:map', config.to_dict())


def flight_config_constructor(loader: yaml.Loader, node: yaml.Node) -> FlightData:
    data = loader.construct_mapping(node, deep=True)
    return FlightData.from_dict(data)


yaml.add_representer(FlightData, flight_config_representer)
yaml.add_constructor('!FlightConfig', flight_config_constructor)
