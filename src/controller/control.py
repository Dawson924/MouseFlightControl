import time

from controller.base import BaseController
from lib.joystick import AXIS_MAX, AXIS_MIN
from utils import check_overflow, wheel_step


class FixedWingController(BaseController):
    def __init__(self, device):
        super().__init__(device)

    def update(self, state, _):
        if state.enabled:
            f = 10
            if state.input.is_pressing(state.options.increase_throttle_speed):
                f = 50
            elif state.input.is_pressing(state.options.decrease_throttle_speed):
                f = 5

            state.Axis.th += wheel_step(
                state.options.throttle_speed * f, -state.input.get_wheel_delta()
            )

            state.Axis.th = check_overflow(state.Axis.th, AXIS_MIN, AXIS_MAX)


class HelicopterController(BaseController):
    def __init__(self, device):
        super().__init__(device)
        self.last_collective_time = 0
        self.last_pedals_time = 0
        self.min_interval = 1.0 / 60

    def update(self, state, _):
        if state.enabled and state.input.alt_ctrl_shift():
            current_time = time.perf_counter()

            # 处理总距调节（W/S键）
            time_since_collective = current_time - self.last_collective_time
            if time_since_collective >= self.min_interval:
                if state.input.is_pressing('W'):
                    state.Axis.th -= state.options.collective_speed
                    state.Axis.th = check_overflow(state.Axis.th, AXIS_MIN, AXIS_MAX)
                    self.last_collective_time = current_time
                elif state.input.is_pressing('S'):
                    state.Axis.th += state.options.collective_speed
                    state.Axis.th = check_overflow(state.Axis.th, AXIS_MIN, AXIS_MAX)
                    self.last_collective_time = current_time

            # 处理尾桨调节（A/D键）
            time_since_pedals = current_time - self.last_pedals_time
            if time_since_pedals >= self.min_interval:
                if state.input.is_pressing('A'):
                    state.Axis.rd -= state.options.pedals_speed
                    state.Axis.rd = check_overflow(state.Axis.rd, AXIS_MIN, AXIS_MAX)
                    self.last_pedals_time = current_time
                elif state.input.is_pressing('D'):
                    state.Axis.rd += state.options.pedals_speed
                    state.Axis.rd = check_overflow(state.Axis.rd, AXIS_MIN, AXIS_MAX)
                    self.last_pedals_time = current_time

            # 重置操作（X/Z键）不受频率限制（瞬时触发）
            if state.input.is_pressed('X'):
                state.Axis.rd = 0
            if state.input.is_pressed('Z'):
                state.Axis.th = AXIS_MAX
