from typing import Any, Callable, Dict, List, Optional


class RuntimeContext:
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._registry = None
        self._env: Optional[Dict[str, Any]] = None

    @property
    def registry(self):
        if self._registry is None:
            from lib.data import registry as global_registry

            self._registry = global_registry
        return self._registry

    @property
    def config(self) -> 'Config':
        return self.registry.get('config')

    @property
    def flight(self) -> 'FlightData':
        return self.registry.get('flightdata')

    @property
    def axis(self) -> 'AxisPos':
        return self.registry.get('axis')

    @property
    def input(self):
        return self.registry.get('input')

    @property
    def indicator(self):
        return self.registry.get('indicator')

    @property
    def main_window(self):
        return self.registry.get('main_window')

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def load_settings(self, plugin_id: str) -> Dict[str, Any]:
        from plugin.config import load_plugin_config

        return load_plugin_config(plugin_id)

    def save_settings(self, plugin_id: str, data: Dict[str, Any]) -> None:
        from plugin.config import save_plugin_config

        save_plugin_config(plugin_id, data)

    def emit(self, event_name: str, *args, **kwargs) -> List[Any]:
        results = []
        for hook in self._hooks.get(event_name, []):
            try:
                result = hook(*args, **kwargs)
                results.append(result)
            except Exception as e:
                from loguru import logger

                logger.exception(f'Hook error in {event_name}: {e}')
        return results

    def on(self, event_name: str, handler: Callable) -> None:
        if event_name not in self._hooks:
            self._hooks[event_name] = []
        self._hooks[event_name].append(handler)

    def off(self, event_name: str, handler: Callable = None) -> None:
        if handler is None:
            self._hooks.pop(event_name, None)
        elif event_name in self._hooks:
            self._hooks[event_name] = [h for h in self._hooks[event_name] if h != handler]


class Extension:
    id: str = ''
    name: str = ''
    version: str = '1.0.0'

    _runtime: Optional[RuntimeContext] = None

    @classmethod
    def get_context(cls) -> RuntimeContext:
        if cls._runtime is None:
            cls._runtime = RuntimeContext()
        return cls._runtime

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.id:
            cls.id = cls.__name__.lower()
        if not cls.name:
            cls.name = cls.__name__

    def get_default_config(self) -> Dict[str, Any]:
        return {}

    def setup(self, runtime: RuntimeContext) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def tick(self, dt: float) -> None:
        pass

    def teardown(self) -> None:
        pass