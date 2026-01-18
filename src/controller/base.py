from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class BaseController(ABC):
    _name: str = ''
    _option_defs: List[tuple]
    _i18n_defs: Dict[str, str]

    def __init__(self, device):
        self.device = device

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
    def add_option(
        cls, name: str, widget: Any, default: Any, i18n_text: Optional[str] = None
    ) -> 'BaseController':
        if not hasattr(cls, '_option_defs'):
            cls._option_defs = []
        if not hasattr(cls, '_i18n_defs'):
            cls._i18n_defs = {}

        for existing_opt in cls._option_defs:
            if existing_opt[0] == name:
                return cls

        cls._option_defs.append((name, widget, default))

        if i18n_text is not None and isinstance(i18n_text, str):
            cls._i18n_defs[name] = i18n_text

        return cls

    @classmethod
    def get_i18n(
        cls, translator: Optional[Callable[[str], str]] = None
    ) -> Dict[str, str]:
        if not hasattr(cls, '_i18n_defs'):
            cls._i18n_defs = {}
        i18n = cls._i18n_defs.copy()
        if translator and callable(translator):
            for key, text in i18n.items():
                i18n[key] = translator(text)
        return i18n

    @abstractmethod
    def update(self, Axis, options, input, state, context):
        pass
