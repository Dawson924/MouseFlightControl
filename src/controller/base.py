from abc import ABC, abstractmethod
from typing import Callable, Optional

from common.axis import AxisPos
from data.flight import FlightInput
from input import InputStateMonitor


class BaseController(ABC):
    _name: str = ''

    def __init__(self, input: FlightInput):
        self.input = input

    @classmethod
    def get_name(cls, translator: Optional[Callable[[str], str]] = None) -> str:
        if not cls._name:
            return cls.__name__
        if translator and callable(translator):
            return translator(cls._name)
        return cls._name

    @abstractmethod
    def update(self, axis: AxisPos, key: InputStateMonitor, state, context):
        pass
