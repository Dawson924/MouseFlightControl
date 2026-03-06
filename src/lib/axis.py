from common.axis import AXIS_LENGTH, AXIS_MAX, AXIS_MIN, AxisPos
from common.constants import FOV_RANGE
from utils import check_overflow


def set_axis(axis: AxisPos, axis_id: str, value: int) -> None:
    setattr(axis, axis_id, check_overflow(value, AXIS_MIN, AXIS_MAX))


def pos(val) -> int:
    val = float(val)
    threshold = 1
    val = 1 if abs(val) < threshold else val
    return int(round(val))


def fov(val, abs=True) -> int:
    f = int(AXIS_LENGTH / FOV_RANGE[1])
    if not abs:
        return val * f
    else:
        return AXIS_MAX - val * f


def axis2fov(val) -> int:
    return (val - AXIS_MIN) / int(AXIS_LENGTH / FOV_RANGE[1])
