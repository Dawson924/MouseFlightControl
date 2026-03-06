from __future__ import annotations

import copy
from typing import Any, Dict, Optional

import yaml


class _YamlMixin:
    """Load from / dump to YAML.  Requires to_dict / from_dict on the subclass."""

    @classmethod
    def from_yaml(
        cls,
        yaml_str: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> '_YamlMixin':
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
        return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)


class FlatConfig(_YamlMixin):
    SPEC: Dict[str, Dict[str, Any]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._flat_spec: Dict[str, Dict[str, Any]] = {}
        cls._field_group: Dict[str, str] = {}
        for group, fields in cls.SPEC.items():
            for field, spec in fields.items():
                cls._flat_spec[field] = spec
                cls._field_group[field] = group

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {
            group: {field: copy.deepcopy(spec['default']) for field, spec in fields.items()}
            for group, fields in self.SPEC.items()
        }

    def _validate(self, field: str, value: Any) -> None:
        if field not in self._flat_spec:
            raise ValueError(f'Unknown field: {field!r}')
        spec = self._flat_spec[field]

        if not isinstance(value, spec['type']):
            raise TypeError(f'{field} must be {spec["type"].__name__}, got {type(value).__name__}')
        if 'min' in spec and value < spec['min']:
            raise ValueError(f'{field} must be >= {spec["min"]} (got {value})')
        if 'max' in spec and value > spec['max']:
            raise ValueError(f'{field} must be <= {spec["max"]} (got {value})')
        if 'allowed' in spec and value not in spec['allowed']:
            raise ValueError(f'{field} must be one of {spec["allowed"]} (got {value!r})')

    def _set(self, field: str, value: Any) -> None:
        """Validate and write one field."""
        self._validate(field, value)
        self._data[self._field_group[field]][field] = value

    def _get(self, field: str, default: Any = None) -> Any:
        group = self._field_group.get(field)
        if group is None:
            return default
        return self._data[group].get(field, default)

    def __getattr__(self, key: str) -> Any:
        if key.startswith('_') or key not in self.__class__._flat_spec:
            raise AttributeError(key)
        return self._data[self._field_group[key]][key]

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith('_') or key not in self.__class__._flat_spec:
            super().__setattr__(key, value)
        else:
            self._set(key, value)

    def set(self, field: str, value: Any) -> None:
        if field in self._flat_spec:
            self._set(field, value)

    def get(self, field: str, default: Any = None) -> Any:
        return self._get(field, default)

    def update(self, **kwargs: Any) -> None:
        for field, value in kwargs.items():
            self.set(field, value)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {group: fields.copy() for group, fields in self._data.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'FlatConfig':
        instance = cls()
        for group, fields in cls.SPEC.items():
            if group in data and isinstance(data[group], dict):
                for field in fields:
                    if field in data[group]:
                        instance._set(field, data[group][field])
        return instance


class Config(_YamlMixin):
    SPEC: Dict[str, Dict[str, Any]] = {}

    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {
            group: {field: copy.deepcopy(spec['default']) for field, spec in fields.items()}
            for group, fields in self.SPEC.items()
        }

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

    def _update_group(self, group: str, fields: Dict[str, Any]) -> None:
        if group not in self.SPEC:
            return
        for field, value in fields.items():
            if field in self.SPEC[group]:
                self._set(group, field, value)

    def set(self, group: str, field: str, value: Any) -> None:
        self._set(group, field, value)

    def get(self, group: str, field: str, default: Any = None) -> Any:
        return self._get(group, field, default)

    def update(self, data: Dict[str, Dict[str, Any]]) -> None:
        for group, fields in data.items():
            if isinstance(fields, dict):
                self._update_group(group, fields)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {group: fields.copy() for group, fields in self._data.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Any]]) -> 'Config':
        instance = cls()
        for group, fields in cls.SPEC.items():
            if group in data and isinstance(data[group], dict):
                for field in fields:
                    if field in data[group]:
                        instance._set(group, field, data[group][field])
        return instance
