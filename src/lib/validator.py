from typing import Any, Dict


class Validator:
    def __init__(self, spec: Dict[str, Dict[str, Any]]):
        self.spec = spec

    def check(self, group: str, field: str, value: Any):
        if group not in self.spec:
            raise ValueError(f'Invalid config group: {group}')
        if field not in self.spec[group]:
            raise ValueError(f'Invalid config field {field} in group {group}')

        spec = self.spec[group][field]

        if not isinstance(value, spec['type']):
            raise TypeError(f'{group}.{field} must be {spec["type"].__name__}, got {type(value).__name__}')

        if 'fields' in spec:
            if not isinstance(value, dict):
                raise TypeError(f'{group}.{field} must be a dictionary')

            for sub_field, sub_spec in spec['fields'].items():
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
