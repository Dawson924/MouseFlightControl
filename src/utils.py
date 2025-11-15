from common.constants import FOV_RANGE
from lib.joystick import AXIS_LENGTH, AXIS_MIN


def check_overflow(a, min_val, max_val):
    if a < min_val:
        return min_val
    elif a > max_val:
        return max_val
    return a


def wheel_step(step, wheel_delta):
    if wheel_delta == 0:
        return 0
    if wheel_delta > 0:
        sign = 1
    else:
        sign = -1
    return sign * step


def pos(val):
    val = float(val)
    threshold = 1
    val = 1 if abs(val) < threshold else val
    return int(round(val))


def fov(val, abs=True):
    f = int(AXIS_LENGTH / FOV_RANGE[1])
    if not abs:
        return val * f
    else:
        return AXIS_MIN + val * f


def axis2fov(val):
    return (val - AXIS_MIN) / int(AXIS_LENGTH / FOV_RANGE[1])
