from controller.base import BaseController
from utils import check_overflow, wheel_step


class FixedWingController(BaseController):
    def __init__(self, vjoy):
        super().__init__(vjoy)

    def update(self, state, _):
        if state.enabled and state.input.alt_ctrl_shift():
            state.Axis.th += wheel_step(state.options.plane_step, -state.input.get_wheel_delta())
            state.Axis.th = check_overflow(state.Axis.th, state.axis_min, state.axis_max)

class HelicopterController(BaseController):
    def __init__(self, vjoy):
        super().__init__(vjoy)

    def update(self, state, _):
        if state.enabled and state.input.alt_ctrl_shift():
            if state.input.is_pressed('X'):
                state.Axis.rd = 0
            if state.input.is_pressed('Z'):
                state.Axis.th = state.axis_max
            if state.input.is_pressing('W'):
                state.Axis.th = state.Axis.th - state.options.heli_step
                state.Axis.th = check_overflow(state.Axis.th, state.axis_min, state.axis_max)
            if state.input.is_pressing('S'):
                state.Axis.th = state.Axis.th + state.options.heli_step
                state.Axis.th = check_overflow(state.Axis.th, state.axis_min, state.axis_max)
            if state.input.is_pressing('A'):
                state.Axis.rd = state.Axis.rd - state.options.heli_step
                state.Axis.rd = check_overflow(state.Axis.rd, state.axis_min, state.axis_max)
            if state.input.is_pressing('D'):
                state.Axis.rd = state.Axis.rd + state.options.heli_step
                state.Axis.rd = check_overflow(state.Axis.rd, state.axis_min, state.axis_max)
