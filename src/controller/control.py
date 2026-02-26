from controller.base import BaseController
from lib.joystick import AXIS_MIN
from type.widget import OptionWidget

MIN_INTERVAL = 1 / 60


class FixedWingController(BaseController):
    _name = 'PlaneController'

    def __init__(self, device, input):
        super().__init__(device, input)
        self.throttle_speed = input.get('throttle_speed')
        self.increase_speed = input.get('increase_speed')
        self.decrease_speed = input.get('decrease_speed')

        self.throttle_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state, _):
        if state.enabled and key.alt_ctrl_shift():
            self.throttle_accumulator += state.dt
            while self.throttle_accumulator >= self.min_interval:
                if key.is_pressing(self.increase_speed):
                    axis.th += self.throttle_speed
                elif key.is_pressing(self.decrease_speed):
                    axis.th -= self.throttle_speed
                self.throttle_accumulator -= self.min_interval


FixedWingController.add_option(
    name='throttle_speed',
    widget=OptionWidget.SpinBox,
    default=100,
    i18n_text='ThrottleSpeed',
).add_option(
    name='increase_speed',
    widget=OptionWidget.LineEdit,
    default='shift',
    i18n_text='IncreaseSpeed',
).add_option(
    name='decrease_speed',
    widget=OptionWidget.LineEdit,
    default='ctrl',
    i18n_text='DecreaseSpeed',
)


class HelicopterController(BaseController):
    _name = 'HelicopterController'

    def __init__(self, device, input):
        super().__init__(device, input)
        self.col_speed = self.input.get('collective_speed')
        self.rud_speed = self.input.get('pedals_speed')
        self.collective_accumulator = 0.0
        self.pedals_accumulator = 0.0
        self.min_interval = MIN_INTERVAL

    def update(self, axis, key, state, _):
        if state.enabled and key.alt_ctrl_shift():
            self.collective_accumulator += state.dt
            self.pedals_accumulator += state.dt

            while self.collective_accumulator >= self.min_interval:
                if key.is_pressing('W'):
                    axis.th += self.col_speed
                elif key.is_pressing('S'):
                    axis.th -= self.col_speed
                self.collective_accumulator -= self.min_interval

            while self.pedals_accumulator >= self.min_interval:
                if key.is_pressing('A'):
                    axis.rd -= self.rud_speed
                elif key.is_pressing('D'):
                    axis.rd += self.rud_speed
                self.pedals_accumulator -= self.min_interval

            if key.is_pressed('X'):
                axis.rd = 0
            if key.is_pressed('Z'):
                axis.th = AXIS_MIN


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
