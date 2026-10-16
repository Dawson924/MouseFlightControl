from abc import ABC, abstractmethod
from typing import Callable, Optional

from common.axis import AxisPos
from data.flight import FlightData
from input import InputDevices
from lib.joystick import AXIS_MIN

MIN_INTERVAL = 1 / 60


class Controller(ABC):
    _name: str = ''
    FIELDS: list = []

    def __init__(self, flightdata: FlightData):
        self.flightdata = flightdata
        self._load_fields()

    def _load_fields(self):
        for field in self.FIELDS:
            setattr(self, field, self.flightdata.get(field))

    @classmethod
    def get_name(cls, translator: Optional[Callable[[str], str]] = None) -> str:
        if not cls._name:
            return cls.__name__
        if translator and callable(translator):
            return translator(cls._name)
        return cls._name

    @abstractmethod
    def update(self, axis: AxisPos, key: InputDevices, state):
        pass


class JetPlaneController(Controller):
    _name = 'JetPlaneController'
    FIELDS = ['thrust_speed', 'throttle_increase', 'throttle_decrease']

    def __init__(self, flightdata):
        super().__init__(flightdata)
        self.throttle_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state):
        if not state.enabled:
            return

        if key.modifiers():
            self.throttle_accumulator += state.dt
            while self.throttle_accumulator >= self.min_interval:
                if key.is_pressing(self.throttle_increase):
                    axis.Throttle += self.thrust_speed
                elif key.is_pressing(self.throttle_decrease):
                    axis.Throttle -= self.thrust_speed
                self.throttle_accumulator -= self.min_interval

        if state.taxiing:
            axis.Rudder = axis.Roll


class HelicopterController(Controller):
    _name = 'HelicopterController'
    FIELDS = [
        'thrust_speed',
        'rudder_speed',
        'collective_increase',
        'collective_decrease',
        'collective_minimum',
        'rudder_left',
        'rudder_right',
        'rudder_center',
    ]

    def __init__(self, flightdata):
        super().__init__(flightdata)
        self.collective_accumulator = 0.0
        self.rudder_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state):
        if not state.enabled:
            return

        if key.modifiers():
            self.collective_accumulator += state.dt
            self.rudder_accumulator += state.dt

            while self.collective_accumulator >= self.min_interval:
                if key.is_pressing(self.collective_increase):
                    axis.Throttle += self.thrust_speed
                elif key.is_pressing(self.collective_decrease):
                    axis.Throttle -= self.thrust_speed
                self.collective_accumulator -= self.min_interval

            while self.rudder_accumulator >= self.min_interval:
                if key.is_pressing(self.rudder_left):
                    axis.Rudder -= self.rudder_speed
                elif key.is_pressing(self.rudder_right):
                    axis.Rudder += self.rudder_speed
                self.rudder_accumulator -= self.min_interval

        if key.is_pressed(self.rudder_center):
            axis.Rudder = 0

        if key.is_pressed(self.collective_minimum):
            axis.Throttle = AXIS_MIN


class PistonPlaneController(Controller):
    _name = 'PistonPlaneController'
    FIELDS = [
        'thrust_speed',
        'throttle_increase',
        'throttle_decrease',
        'rudder_left',
        'rudder_right',
        'rudder_center',
    ]

    def __init__(self, flightdata):
        super().__init__(flightdata)
        self.throttle_accumulator = 0.0
        self.rudder_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state):
        if not state.enabled:
            return

        if key.modifiers():
            self.throttle_accumulator += state.dt
            self.rudder_accumulator += state.dt

            while self.throttle_accumulator >= self.min_interval:
                if key.is_pressing(self.throttle_increase):
                    axis.Throttle += self.thrust_speed
                elif key.is_pressing(self.throttle_decrease):
                    axis.Throttle -= self.thrust_speed
                self.throttle_accumulator -= self.min_interval

            while self.rudder_accumulator >= self.min_interval:
                if key.is_pressing(self.rudder_left):
                    axis.Rudder -= self.rudder_speed
                elif key.is_pressing(self.rudder_right):
                    axis.Rudder += self.rudder_speed
                self.rudder_accumulator -= self.min_interval

        if key.is_pressed(self.rudder_center):
            axis.Rudder = 0
