import threading
from typing import Any, Optional


class DataStore:
    _instance: Optional['DataStore'] = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data = {}
                    cls._instance._singletons = {}
        return cls._instance

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._data:
                return self._data[key]
            elif key in self._singletons:
                return self._singletons[key]
            return default

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._data:
                del self._data[key]

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def singleton(self, name: str, instance: Any) -> None:
        with self._lock:
            self._singletons[name] = instance

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._data or key in self._singletons

    def keys(self) -> list:
        with self._lock:
            return list(self._data.keys())

    def values(self) -> list:
        with self._lock:
            return list(self._data.values())

    def items(self) -> list:
        with self._lock:
            return list(self._data.items())


store = DataStore()
