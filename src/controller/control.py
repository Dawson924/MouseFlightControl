from controller.base import BaseController
from lib.joystick import AXIS_MIN
from type.widget import OptionWidget
from utils import wheel_step


class FixedWingController(BaseController):
    _name = 'PlaneController'

    def __init__(self, device):
        super().__init__(device)

    def update(self, Axis, options, input, state, _):
        if state.enabled:
            f = 10
            if input.is_pressing(options.increase_throttle_speed):
                f = 50
            elif input.is_pressing(options.decrease_throttle_speed):
                f = 5

            Axis.th += wheel_step(options.throttle_speed * f, input.get_wheel_delta())


FixedWingController.add_option(
    name='throttle_speed',
    widget=OptionWidget.SpinBox,
    default=100,
    i18n_text='ThrottleSpeed',
).add_option(
    name='increase_throttle_speed',
    widget=OptionWidget.LineEdit,
    default='shift',
    i18n_text='IncreaseSpeed',
).add_option(
    name='decrease_throttle_speed',
    widget=OptionWidget.LineEdit,
    default='ctrl',
    i18n_text='DecreaseSpeed',
)


class HelicopterController(BaseController):
    _name = 'HelicopterController'

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
                    Axis.th += options.collective_speed
                elif input.is_pressing('S'):
                    Axis.th -= options.collective_speed
                self.collective_accumulator -= self.min_interval

            while self.pedals_accumulator >= self.min_interval:
                if input.is_pressing('A'):
                    Axis.rd -= options.pedals_speed
                elif input.is_pressing('D'):
                    Axis.rd += options.pedals_speed
                self.pedals_accumulator -= self.min_interval

            if input.is_pressed('X'):
                Axis.rd = 0
            if input.is_pressed('Z'):
                Axis.th = AXIS_MIN


HelicopterController.add_option(
    name='collective_speed',
    widget=OptionWidget.SpinBox,
    default=125,
    i18n_text='CollectiveSpeed',
).add_option(
    name='pedals_speed',
    widget=OptionWidget.SpinBox,
    default=125,
    i18n_text='RudderSpeed',
)
