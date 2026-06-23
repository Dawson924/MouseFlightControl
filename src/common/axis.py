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

CONTROL_AXES = ['Roll', 'Pitch', 'Throttle', 'CamX', 'CamY', 'Rudder', 'ZoomView']
JOYSTICK_AXES = ['X', 'Y', 'Z', 'Rx', 'Ry', 'Rz', 'Sl', 'Sl2']


# Type definitions
ControlAxis = Literal['Roll', 'Pitch', 'Throttle', 'CamX', 'CamY', 'Rudder', 'ZoomView']
JoystickAxis = Literal['X', 'Y', 'Z', 'Rx', 'Ry', 'Rz', 'Sl', 'Sl2']


class AxisPos:
    def __init__(self, Roll, Pitch, Throttle, Rudder, CamX, CamY, ZoomView):
        self.Roll = Roll
        self.Pitch = Pitch
        self.Throttle = Throttle
        self.Rudder = Rudder
        self.CamX = CamX
        self.CamY = CamY
        self.ZoomView = ZoomView
