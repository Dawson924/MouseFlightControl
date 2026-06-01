from controller.base import BaseController
from lib.joystick import AXIS_MIN

MIN_INTERVAL = 1 / 60


class FixedWingController(BaseController):
    _name = 'PlaneController'

    def __init__(self, input):
        super().__init__(input)
        self.thrust_speed = input.get('thrust_speed')
        self.throttle_increase = input.get('throttle_increase')
        self.throttle_decrease = input.get('throttle_decrease')

        self.throttle_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state, _):
        if state.enabled and key.alt_ctrl_shift():
            self.throttle_accumulator += state.dt
            while self.throttle_accumulator >= self.min_interval:
                if key.is_pressing(self.throttle_increase):
                    axis.th += self.thrust_speed
                elif key.is_pressing(self.throttle_decrease):
                    axis.th -= self.thrust_speed
                self.throttle_accumulator -= self.min_interval


class HelicopterController(BaseController):
    _name = 'HelicopterController'

    def __init__(self, input):
        super().__init__(input)
        self.col_speed = self.input.get('thrust_speed')
        self.rud_speed = self.input.get('rudder_speed')
        self.col_increase = self.input.get('collective_increase')
        self.col_decrease = self.input.get('collective_decrease')
        self.rud_left = self.input.get('rudder_left')
        self.rud_right = self.input.get('rudder_right')
        self.collective_accumulator = 0.0
        self.pedals_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state, _):
        if state.enabled and key.alt_ctrl_shift():
            self.collective_accumulator += state.dt
            self.pedals_accumulator += state.dt

            while self.collective_accumulator >= self.min_interval:
                if key.is_pressing(self.col_increase):
                    axis.th += self.col_speed
                elif key.is_pressing(self.col_decrease):
                    axis.th -= self.col_speed
                self.collective_accumulator -= self.min_interval

            while self.pedals_accumulator >= self.min_interval:
                if key.is_pressing(self.rud_left):
                    axis.rd -= self.rud_speed
                elif key.is_pressing(self.rud_right):
                    axis.rd += self.rud_speed
                self.pedals_accumulator -= self.min_interval

            if key.is_pressed('X'):
                axis.th = AXIS_MIN
