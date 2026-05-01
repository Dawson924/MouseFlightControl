from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from common.axis import AxisPos
from data.flight import FlightInput
from input import InputStateMonitor


class BaseController(ABC):
    _name: str = ''
    _option_defs: List[tuple]
    _i18n_defs: Dict[str, str]

    def __init__(self, input: FlightInput):
        self.input = input

    @classmethod
    def get_name(cls, translator: Optional[Callable[[str], str]] = None) -> str:
        if not cls._name:
            return cls.__name__
        if translator and callable(translator):
            return translator(cls._name)
        return cls._name

    @classmethod
    def get_options(cls) -> List[tuple]:
        if not hasattr(cls, '_option_defs'):
            cls._option_defs = []
        return cls._option_defs.copy()

    @classmethod
    def add_option(cls, id: str, widget: Any, default: Any, i18n: Optional[str] = None) -> 'BaseController':
        if not hasattr(cls, '_option_defs'):
            cls._option_defs = []
        if not hasattr(cls, '_i18n_defs'):
            cls._i18n_defs = {}

        for _option_def in cls._option_defs:
            if _option_def[0] == id:
                return cls

        cls._option_defs.append((id, widget, default))

        if i18n is not None and isinstance(i18n, str):
            cls._i18n_defs[id] = i18n

        return cls

    @classmethod
    def get_i18n(cls, translator: Optional[Callable[[str], str]] = None) -> Dict[str, str]:
        if not hasattr(cls, '_i18n_defs'):
            cls._i18n_defs = {}
        i18n = cls._i18n_defs.copy()
        if translator and callable(translator):
            for key, text in i18n.items():
                i18n[key] = translator(text)
        return i18n

    @abstractmethod
    def update(self, axis: AxisPos, key: InputStateMonitor, state, context):
        pass
