from controller.base import BaseController
from lib.joystick import AXIS_MAX, AXIS_MIN
from utils import check_overflow, wheel_step


class FixedWingController(BaseController):
    def __init__(self, device):
        super().__init__(device)

    def update(self, Axis, options, input, state, _):
        if state.enabled:
            f = 10
            if input.is_pressing(options.increase_throttle_speed):
                f = 50
            elif input.is_pressing(options.decrease_throttle_speed):
                f = 5

            Axis.th += wheel_step(options.throttle_speed * f, -input.get_wheel_delta())

            Axis.th = check_overflow(Axis.th, AXIS_MIN, AXIS_MAX)


class HelicopterController(BaseController):
    def __init__(self, device):
        super().__init__(device)
        self.collective_accumulator = 0.0
        self.pedals_accumulator = 0.0
        self.min_interval = 1.0 / 60

    def update(self, Axis, options, input, state, _):
        if state.enabled and input.alt_ctrl_shift():
            self.collective_accumulator += state.dt
            self.pedals_accumulator += state.dt

            while self.collective_accumulator >= self.min_interval:
                if input.is_pressing('W'):
                    Axis.th -= options.collective_speed
                    Axis.th = check_overflow(Axis.th, AXIS_MIN, AXIS_MAX)
                elif input.is_pressing('S'):
                    Axis.th += options.collective_speed
                    Axis.th = check_overflow(Axis.th, AXIS_MIN, AXIS_MAX)
                self.collective_accumulator -= self.min_interval

            while self.pedals_accumulator >= self.min_interval:
                if input.is_pressing('A'):
                    Axis.rd -= options.pedals_speed
                    Axis.rd = check_overflow(Axis.rd, AXIS_MIN, AXIS_MAX)
                elif input.is_pressing('D'):
                    Axis.rd += options.pedals_speed
                    Axis.rd = check_overflow(Axis.rd, AXIS_MIN, AXIS_MAX)
                self.pedals_accumulator -= self.min_interval

            if input.is_pressed('X'):
                Axis.rd = 0
            if input.is_pressed('Z'):
                Axis.th = AXIS_MAX
