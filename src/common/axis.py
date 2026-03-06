from typing import Literal

AXIS_MAX = 32767
AXIS_MIN = -32768
AXIS_LENGTH = 65535
AXIS_CENTER = 0

AXIS_X = 'x'
AXIS_Y = 'y'
AXIS_Z = 'z'
AXIS_RX = 'rx'
AXIS_RY = 'ry'
AXIS_RZ = 'rz'
AXIS_SL = 'sl'
AXIS_SL2 = 'sl2'

AxisName = Literal['x', 'y', 'z', 'rx', 'ry', 'rz', 'sl', 'sl2']


class AxisPos:
    def __init__(self, x, y, th, rd, vx, vy, vz):
        self.x, self.y, self.th, self.rd = x, y, th, rd
        self.vx, self.vy, self.vz = vx, vy, vz
