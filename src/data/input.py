from typing import Any, Dict

import yaml

from type.axis import AxisName
from type.filter import Filter

AXIS_NAMES = ['x', 'y', 'z', 'rx', 'ry', 'rz', 'sl', 'sl2']

INPUT_META: Dict[str, Dict[str, Any]] = {
    'Input': {
        'flight_mode': {'type': int, 'allowed': [-1, 0, 1, 2], 'default': 0},
        'camera_fov': {'type': int, 'min': 60, 'max': 160, 'default': 100},
        'throttle_speed': {'type': int, 'min': 100, 'max': 1000, 'default': 160},
        'collective_speed': {'type': int, 'min': 100, 'max': 1000, 'default': 140},
        'pedals_speed': {'type': int, 'min': 100, 'max': 1000, 'default': 120},
        'increase_speed': {'type': str, 'default': ''},
        'decrease_speed': {'type': str, 'default': ''},
    },
    'Axis': {
        axis_name: {
            'type': dict,
            'default': {'invert': False if axis_name not in ['z', 'sl'] else True, 'curvature': 0.0, 'deadzone': 0.0},
            'field_specs': {
                'invert': {'type': bool},
                'curvature': {'type': float, 'min': -1.0, 'max': 1.0},
                'deadzone': {'type': float, 'min': 0.0, 'max': 1.0},
            },
        }
        for axis_name in AXIS_NAMES
    },
}

DEFAULT_GROUP = 'Input'


class FlightInput:
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        for group, fields in INPUT_META.items():
            self._data[group] = {}
            for field, spec in fields.items():
                self._data[group][field] = spec['default']

    def _validate_value(self, group: str, field: str, value: Any):
        if group not in INPUT_META:
            raise ValueError(f'Invalid config group: {group}')
        if field not in INPUT_META[group]:
            raise ValueError(f'Invalid config field {field} in group {group}')

        spec = INPUT_META[group][field]

        if not isinstance(value, spec['type']):
            raise TypeError(f'{group}.{field} must be {spec["type"].__name__}, got {type(value).__name__}')

        if group == 'Axis' and 'field_specs' in spec:
            if not isinstance(value, dict):
                raise TypeError(f'{group}.{field} must be a dictionary')

            for sub_field, sub_spec in spec['field_specs'].items():
                if sub_field not in value:
                    raise ValueError(f'{group}.{field} must contain "{sub_field}" field')

                sub_value = value[sub_field]
                if not isinstance(sub_value, sub_spec['type']):
                    raise TypeError(
                        f'{group}.{field}.{sub_field} must be {sub_spec["type"].__name__}, got {type(sub_value).__name__}'
                    )

                if 'min' in sub_spec and sub_value < sub_spec['min']:
                    raise ValueError(f'{group}.{field}.{sub_spec} must be >= {sub_spec["min"]} (got {sub_value})')
                if 'max' in sub_spec and sub_value > sub_spec['max']:
                    raise ValueError(f'{group}.{field}.{sub_spec} must be <= {sub_spec["max"]} (got {sub_value})')
        else:
            if 'min' in spec and value < spec['min']:
                raise ValueError(f'{group}.{field} must be >= {spec["min"]} (got {value})')
            if 'max' in spec and value > spec['max']:
                raise ValueError(f'{group}.{field} must be <= {spec["max"]} (got {value})')

            if 'allowed' in spec and value not in spec['allowed']:
                raise ValueError(f'{group}.{field} must be one of {spec["allowed"]} (got {value})')

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {group: fields.copy() for group, fields in self._data.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'FlightInput':
        config = cls()
        for group, fields in INPUT_META.items():
            if group in data and isinstance(data[group], dict):
                for field in fields.keys():
                    if field in data[group]:
                        config._validate_value(group, field, data[group][field])
                        config._data[group][field] = data[group][field]
        return config

    @classmethod
    def from_yaml(cls, yaml_str: str = None, file_path: str = None) -> 'FlightInput':
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
        elif yaml_str:
            raw_data = yaml.safe_load(yaml_str)
        else:
            raise ValueError('Must provide either yaml_str or file_path')

        if isinstance(raw_data, FlightInput):
            return raw_data
        return cls.from_dict(raw_data)

    def update(self, data: Dict[str, Dict[str, Any]]):
        for group, fields in data.items():
            if group in INPUT_META and isinstance(fields, dict):
                for field, value in fields.items():
                    if field in INPUT_META[group]:
                        self._validate_value(group, field, value)
                        self._data[group][field] = value

    def has(self, field: str) -> bool:
        return field in INPUT_META[DEFAULT_GROUP]

    def set(self, field: str, value: Any):
        self._data[DEFAULT_GROUP][field] = value

    def get(self, field: str, default: Any = None) -> Any:
        return self._data.get(DEFAULT_GROUP, {}).get(field, default)

    def get_filters(self):
        return {k: Filter.from_dict(v) for k, v in self._data['Axis'].items()}

    def get_filter(self, axis_id: AxisName):
        return Filter.from_dict(self._data['Axis'][axis_id])

    def set_filter(self, axis_id: AxisName, filter: Filter):
        self._data['Axis'][axis_id] = filter.to_dict()

    def __getitem__(self, key: str) -> Any:
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value


def flight_config_representer(dumper: yaml.Dumper, config: FlightInput) -> yaml.Node:
    return dumper.represent_mapping('tag:yaml.org,2002:map', config.to_dict())


def flight_config_constructor(loader: yaml.Loader, node: yaml.Node) -> FlightInput:
    data = loader.construct_mapping(node, deep=True)
    return FlightInput.from_dict(data)


yaml.add_representer(FlightInput, flight_config_representer)
yaml.add_constructor('!FlightConfig', flight_config_constructor)
