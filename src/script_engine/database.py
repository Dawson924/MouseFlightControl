import threading
from copy import deepcopy
from typing import Any, Dict, List, Optional


class ScriptDatabase:
    _instance: Optional['ScriptDatabase'] = None
    _initialized: bool = False
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, initial_data: Optional[Dict[str, Dict[str, Any]]] = None):
        if not self._initialized:
            self._tables = deepcopy(initial_data) if initial_data else {}
            self._initialized = True

    def get(self, table_name: str, default: Any = None) -> Dict[str, Any]:
        return self._tables.get(table_name, default)

    def list_tables(self) -> List[str]:
        return list(self._tables.keys())

    def add(
        self, table_name: str, table_data: Dict[str, Any], overwrite: bool = False
    ) -> None:
        if table_name in self._tables and not overwrite:
            raise ValueError(f"Table '{table_name}' exists")
        self._tables[table_name] = deepcopy(table_data)

    def update(self, table_name: str, new_data: Dict[str, Any]) -> None:
        if table_name not in self._tables:
            self._tables[table_name] = {}
        self._tables[table_name].update(new_data)

    def delete(self, table_name: str) -> None:
        self._tables.pop(table_name, None)

    def delete_key(self, table_name: str, key: str) -> None:
        if table_name in self._tables:
            self._tables[table_name].pop(key, None)

    def reset(self, initial_data: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        with self._lock:
            self._tables = deepcopy(initial_data) if initial_data else {}

    def to_dict(self, copy: bool = True) -> Dict[str, Dict[str, Any]]:
        if copy:
            return deepcopy(self._tables)
        return self._tables

    def __repr__(self) -> str:
        table_info = ', '.join(
            f"'{name}': {len(data)} keys" for name, data in self._tables.items()
        )
        return f'ScriptDatabase(singleton, tables=[{table_info}])'
