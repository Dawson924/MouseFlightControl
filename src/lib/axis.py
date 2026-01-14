from common.constants import FOV_RANGE
from lib.joystick import AXIS_LENGTH, AXIS_MAX, AXIS_MIN
from type.axis import AxisPos
from utils import check_overflow


def set_axis(axis: AxisPos, axis_id: str, value: int):
    setattr(axis, axis_id, check_overflow(value, AXIS_MIN, AXIS_MAX))


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
        return AXIS_MAX - val * f


def axis2fov(val):
    return (val - AXIS_MIN) / int(AXIS_LENGTH / FOV_RANGE[1])
