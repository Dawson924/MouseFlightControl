from __future__ import annotations

import copy
from typing import Any, Dict, Optional

import yaml


class YamlStorage:
    SPEC: Dict[str, Dict[str, Any]] = {}
    DEFAULT_GROUP: Optional[str] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._field_group: Dict[str, str] = {}
        for group, fields in cls.SPEC.items():
            for field in fields:
                cls._field_group[field] = group

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {
            group: {field: copy.deepcopy(spec['default']) for field, spec in fields.items()}
            for group, fields in self.SPEC.items()
        }

    def _resolve_group(self, field: str) -> Optional[str]:
        if self.DEFAULT_GROUP is not None:
            return self.DEFAULT_GROUP
        return self._field_group.get(field)

    def _validate(self, group: str, field: str, value: Any) -> None:
        if group not in self.SPEC:
            raise ValueError(f'Unknown group: {group!r}')
        if field not in self.SPEC[group]:
            raise ValueError(f'Unknown field {field!r} in group {group!r}')

        spec = self.SPEC[group][field]

        if not isinstance(value, spec['type']):
            raise TypeError(f'{group}.{field} must be {spec["type"].__name__}, got {type(value).__name__}')

        if 'fields' in spec:
            if not isinstance(value, dict):
                raise TypeError(f'{group}.{field} must be a dictionary')
            for sub_field, sub_spec in spec['fields'].items():
                if sub_field not in value:
                    raise ValueError(f'{group}.{field} must contain {sub_field!r}')
                sub_value = value[sub_field]
                if not isinstance(sub_value, sub_spec['type']):
                    raise TypeError(
                        f'{group}.{field}.{sub_field} must be '
                        f'{sub_spec["type"].__name__}, got {type(sub_value).__name__}'
                    )
                if 'min' in sub_spec and sub_value < sub_spec['min']:
                    raise ValueError(f'{group}.{field}.{sub_field} must be >= {sub_spec["min"]} (got {sub_value})')
                if 'max' in sub_spec and sub_value > sub_spec['max']:
                    raise ValueError(f'{group}.{field}.{sub_field} must be <= {sub_spec["max"]} (got {sub_value})')
        else:
            if 'min' in spec and value < spec['min']:
                raise ValueError(f'{group}.{field} must be >= {spec["min"]} (got {value})')
            if 'max' in spec and value > spec['max']:
                raise ValueError(f'{group}.{field} must be <= {spec["max"]} (got {value})')
            if 'allowed' in spec and value not in spec['allowed']:
                raise ValueError(f'{group}.{field} must be one of {spec["allowed"]} (got {value!r})')

    def _set(self, group: str, field: str, value: Any) -> None:
        self._validate(group, field, value)
        self._data[group][field] = value

    def _get(self, group: str, field: str, default: Any = None) -> Any:
        return self._data.get(group, {}).get(field, default)

    def __getattr__(self, key: str) -> Any:
        if key.startswith('_') or key not in self.__class__._field_group:
            raise AttributeError(key)
        group = self.__class__._field_group[key]
        return self._data[group][key]

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith('_') or key not in self.__class__._field_group:
            super().__setattr__(key, value)
        else:
            group = self.__class__._field_group[key]
            self._set(group, key, value)

    def __getitem__(self, key: str) -> Any:
        if key in self._field_group:
            group = self._field_group[key]
            return self._data[group][key]
        return self._data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self._field_group:
            group = self._field_group[key]
            self._set(group, key, value)
        else:
            self._data[key] = value

    def set(self, field: str, value: Any) -> None:
        group = self._resolve_group(field)
        if group is not None:
            self._set(group, field, value)

    def get(self, field: str, default: Any = None) -> Any:
        group = self._resolve_group(field)
        if group is not None:
            return self._get(group, field, default)
        return default

    def update(self, *args, **kwargs: Any) -> None:
        if args and isinstance(args[0], dict):
            data = args[0]
            if any(isinstance(v, dict) for v in data.values()):
                for group, fields in data.items():
                    if isinstance(fields, dict):
                        for field, value in fields.items():
                            if group in self.SPEC and field in self.SPEC[group]:
                                try:
                                    self._set(group, field, value)
                                except (ValueError, TypeError):
                                    pass
            else:
                for field, value in data.items():
                    group = self._resolve_group(field)
                    if group is not None:
                        try:
                            self._set(group, field, value)
                        except (ValueError, TypeError):
                            pass
        for field, value in kwargs.items():
            group = self._resolve_group(field)
            if group is not None:
                try:
                    self._set(group, field, value)
                except (ValueError, TypeError):
                    pass

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {group: fields.copy() for group, fields in self._data.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'YamlStorage':
        instance = cls()
        for group, fields in cls.SPEC.items():
            if group in data and isinstance(data[group], dict):
                for field in fields:
                    if field in data[group]:
                        try:
                            instance._set(group, field, data[group][field])
                        except (ValueError, TypeError):
                            pass
        return instance

    @classmethod
    def from_yaml(
        cls,
        yaml_str: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> 'YamlStorage':
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw = yaml.safe_load(f)
        elif yaml_str:
            raw = yaml.safe_load(yaml_str)
        else:
            raise ValueError('Must provide either yaml_str or file_path')

        if isinstance(raw, cls):
            return raw
        return cls.from_dict(raw)

    def to_yaml(self) -> str:
        data = self.to_dict()

        result = []

        first_section = True
        for section in self.SPEC:
            if section not in data:
                continue

            if not first_section:
                result.append('')
            first_section = False

            result.append(f'{section}:')

            section_data = data[section]
            if isinstance(section_data, dict):
                if section == 'Joystick':
                    first_axis = True
                    for axis in self.SPEC[section]:
                        if axis not in section_data:
                            continue

                        if not first_axis:
                            result.append('')
                        first_axis = False

                        result.append(f'  {axis}:')

                        axis_data = section_data[axis]
                        for key in self.SPEC[section][axis].get('fields', {}):
                            if key in axis_data:
                                value = axis_data[key]
                                if isinstance(value, str):
                                    if any(c in value for c in '`\'"\n\r'):
                                        result.append(f"    {key}: '{value}'")
                                    else:
                                        result.append(f'    {key}: {value}')
                                else:
                                    result.append(f'    {key}: {value}')
                else:
                    for field in self.SPEC[section]:
                        if field in section_data:
                            value = section_data[field]
                            if isinstance(value, str):
                                if any(c in value for c in '`\'"\n\r'):
                                    result.append(f"  {field}: '{value}'")
                                else:
                                    result.append(f'  {field}: {value}')
                            else:
                                result.append(f'  {field}: {value}')

        return '\n'.join(result) + '\n'
