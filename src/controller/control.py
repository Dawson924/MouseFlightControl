import time
from controller.base import BaseController
from utils import check_overflow, wheel_step

class FixedWingController(BaseController):
    def __init__(self, vjoy):
        super().__init__(vjoy)

    def update(self, state, _):
        if state.enabled:
            f = 10
            if state.input.alt_ctrl_shift(shift=True):
                f = 50
            elif state.input.alt_ctrl_shift(ctrl=True):
                f = 5
            state.Axis.th += wheel_step(state.options.throttle_speed * f, -state.input.get_wheel_delta())
            state.Axis.th = check_overflow(state.Axis.th, state.axis_min, state.axis_max)

class HelicopterController(BaseController):
    def __init__(self, vjoy):
        super().__init__(vjoy)
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
                    state.Axis.th = check_overflow(state.Axis.th, state.axis_min, state.axis_max)
                    self.last_collective_time = current_time
                elif state.input.is_pressing('S'):
                    state.Axis.th += state.options.collective_speed
                    state.Axis.th = check_overflow(state.Axis.th, state.axis_min, state.axis_max)
                    self.last_collective_time = current_time

            # 处理尾桨调节（A/D键）
            time_since_pedals = current_time - self.last_pedals_time
            if time_since_pedals >= self.min_interval:
                if state.input.is_pressing('A'):
                    state.Axis.rd -= state.options.pedals_speed
                    state.Axis.rd = check_overflow(state.Axis.rd, state.axis_min, state.axis_max)
                    self.last_pedals_time = current_time
                elif state.input.is_pressing('D'):
                    state.Axis.rd += state.options.pedals_speed
                    state.Axis.rd = check_overflow(state.Axis.rd, state.axis_min, state.axis_max)
                    self.last_pedals_time = current_time

            # 重置操作（X/Z键）不受频率限制（瞬时触发）
            if state.input.is_pressed('X'):
                state.Axis.rd = 0
            if state.input.is_pressed('Z'):
                state.Axis.th = state.axis_max
