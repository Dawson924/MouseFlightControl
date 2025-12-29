import ctypes
import logging
from abc import ABC, abstractmethod
from os import path
from typing import Any, Dict, Literal

from common.constants import DLL_PATH
from type.curve import Filter

AXIS_MAX = 32767
AXIS_MIN = -32768
AXIS_LENGTH = 65535
AXIS_CENTER = 0

HID_X = 0x30  # X轴
HID_Y = 0x31  # Y轴
HID_Z = 0x32  # Z轴
HID_RX = 0x33  # X旋转轴
HID_RY = 0x34  # Y旋转轴
HID_RZ = 0x35  # Z旋转轴
HID_SLIDER = 0x36  # 滑块1
HID_WHEEL = 0x38  # 滚轮


DeviceType = Literal['vjoy', 'xbox']


def get_joystick_device(device: DeviceType, device_id: int = 1):
    if device == 'vjoy':
        return VJoyDevice(device_id, path.join(DLL_PATH, 'joystickinput.dll'))
    elif device == 'xbox':
        return XboxDevice(path.join(DLL_PATH, 'joystickinput.dll'))


class JoystickInput:
    def __init__(self, dll_path: str):
        try:
            self.dll = ctypes.CDLL(dll_path)
            self.dll_path = dll_path
        except OSError as e:
            raise RuntimeError(f'Invalid shared library: {dll_path}') from e

        self._declare()

    def _declare(self):
        self.dll.vjoy.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.dll.vjoy.restype = ctypes.c_int32

    def vjoy(self, val: int) -> int:
        if not isinstance(val, int):
            raise TypeError(f'Unexpected type: {type(val)}')
        try:
            return self.dll.vjoy(val, AXIS_MIN, AXIS_MAX)
        except OSError as e:
            raise RuntimeError(e) from e

    def __del__(self):
        if hasattr(self, 'dll'):
            try:
                ctypes.windll.kernel32.FreeLibrary(self.dll._handle)
            except Exception:
                pass


class JoystickDevice(ABC):
    def __init__(self, dll_path: str):
        self.device = None
        self.input = JoystickInput(dll_path)
        self.axis_mapping = self.get_axis_mapping()
        self.button_mapping = self.get_button_mapping()
        self.curve_filters = {}

    @abstractmethod
    def get_axis_mapping(self) -> Dict[int, Any]:
        pass

    @abstractmethod
    def get_button_mapping(self) -> Dict[int, Any]:
        pass

    @abstractmethod
    def init_device(self) -> None:
        pass

    @abstractmethod
    def convert(self, axis_id: int, value: int) -> Any:
        pass

    @abstractmethod
    def _set_axis(self, axis: Any, value: Any) -> None:
        pass

    @abstractmethod
    def _set_button(self, button: Any, pressed: bool) -> None:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    def set_filter(self, axis: int, filter: Filter) -> None:
        self.curve_filters[axis] = filter

    def set_axis(self, axis: int, value: int) -> bool:
        if axis not in self.axis_mapping:
            # logging.warning(
            #     f'Unsupported axis ID {axis} (device type: {self.__class__.__name__})'
            # )
            return False

        filter = self.curve_filters.get(axis)
        if filter:
            if filter.invert:
                value = -value

        try:
            self.init_device()
            value = self.convert(axis, value)
            axis = self.axis_mapping[axis]
            self._set_axis(axis, value)
            return True
        except RuntimeError as e:
            raise e
        except Exception as e:
            logging.error(f'Failed to set axis {axis}: {str(e)}')
            return False

    def set_button(self, button_id: int, pressed: bool) -> bool:
        if button_id not in self.button_mapping:
            logging.warning(
                f'Unsupported button ID {button_id} (device type: {self.__class__.__name__})'
            )
            return False

        try:
            self.init_device()
            target_btn = self.button_mapping[button_id]
            self._set_button(target_btn, pressed)
            return True
        except Exception as e:
            logging.error(f'Failed to set button {button_id}: {str(e)}')
            return False


class VJoyDevice(JoystickDevice):
    def __init__(self, device_id: int, dll_path: str):
        self.device_id = device_id
        try:
            import pyvjoy

            self._pyvjoy = pyvjoy
        except ImportError as e:
            raise RuntimeError(f'Failed to import pyvjoy module: {e}') from e
        super().__init__(dll_path)

    def get_axis_mapping(self) -> Dict[int, Any]:
        return {
            HID_X: self._pyvjoy.HID_USAGE_X,
            HID_Y: self._pyvjoy.HID_USAGE_Y,
            HID_Z: self._pyvjoy.HID_USAGE_Z,
            HID_RX: self._pyvjoy.HID_USAGE_RX,
            HID_RY: self._pyvjoy.HID_USAGE_RY,
            HID_RZ: self._pyvjoy.HID_USAGE_RZ,
            HID_SLIDER: self._pyvjoy.HID_USAGE_SL0,
            HID_WHEEL: self._pyvjoy.HID_USAGE_WHL,
        }

    def get_button_mapping(self) -> Dict[int, int]:
        return {i: i for i in range(1, 129)}

    def init_device(self) -> None:
        if self.device is not None:
            return
        try:
            self.device = self._pyvjoy.VJoyDevice(self.device_id)
        except Exception as e:
            raise RuntimeError(
                f'vjoy device initialization failed (ID: {self.device_id}): {str(e)}'
            )

    def convert(self, axis_id: int, value: int) -> int:
        clamped = max(AXIS_MIN, min(AXIS_MAX, value))
        return self.input.vjoy(clamped)

    def _set_axis(self, axis: Any, value: int) -> None:
        self.device.set_axis(axis, value)

    def _set_button(self, target_btn: int, pressed: bool) -> None:
        self.device.set_button(target_btn, pressed)

    def reset(self) -> None:
        try:
            self.init_device()
            self.device.reset()
            self.device.reset_buttons()
        except Exception as e:
            logging.error(f'Failed to reset device: {str(e)}')


class XboxDevice(JoystickDevice):
    def __init__(self, dll_path: str):
        try:
            from vgamepad import XUSB_BUTTON, VX360Gamepad

            self._vgamepad_cls = VX360Gamepad
            self._xusb_button = XUSB_BUTTON
        except ImportError as e:
            raise RuntimeError(f'Failed to import vgamepad module: {e}') from e
        super().__init__(dll_path)
        self.left_joystick = [AXIS_CENTER, AXIS_CENTER]
        self.right_joystick = [AXIS_CENTER, AXIS_CENTER]

    def get_axis_mapping(self) -> Dict[int, str]:
        return {
            HID_X: ('left_joystick', 'x'),  # 左摇杆X轴
            HID_Y: ('left_joystick', 'y'),  # 左摇杆Y轴
            HID_Z: ('right_joystick', 'y'),  # 右摇杆Y轴
            HID_RZ: ('right_joystick', 'x'),  # 右摇杆X轴
        }

    def get_button_mapping(self) -> Dict[int, Any]:
        return {
            1: self._xusb_button.XUSB_GAMEPAD_A,
            2: self._xusb_button.XUSB_GAMEPAD_B,
            3: self._xusb_button.XUSB_GAMEPAD_X,
            4: self._xusb_button.XUSB_GAMEPAD_Y,
            5: self._xusb_button.XUSB_GAMEPAD_LEFT_SHOULDER,
            6: self._xusb_button.XUSB_GAMEPAD_RIGHT_SHOULDER,
            7: self._xusb_button.XUSB_GAMEPAD_BACK,
            8: self._xusb_button.XUSB_GAMEPAD_START,
            9: self._xusb_button.XUSB_GAMEPAD_LEFT_THUMB,
            10: self._xusb_button.XUSB_GAMEPAD_RIGHT_THUMB,
        }

    def init_device(self) -> None:
        if self.device is not None:
            return
        try:
            self.device = self._vgamepad_cls()
        except Exception as e:
            raise RuntimeError(
                f'Xbox controller initialization failed (ViGEmBus driver not installed): {str(e)}\n'
                'Solution: Install ViGEmBus driver (https://github.com/ViGEm/ViGEmBus/releases) and restart'
            ) from e

    def convert(self, _: int, value: int) -> float:
        clamped = max(AXIS_MIN, min(AXIS_MAX, value))
        return clamped

    def _set_axis(self, axis: str, value: float) -> None:
        axis_type, dir = axis
        if axis_type == 'left_joystick':
            self.left_joystick[0 if dir == 'x' else 1] = value if dir == 'x' else -value
            self.device.left_joystick(self.left_joystick[0], self.left_joystick[1])
        elif axis_type == 'right_joystick':
            self.right_joystick[0 if dir == 'x' else 1] = (
                value if dir == 'x' else -value
            )
            self.device.right_joystick(self.right_joystick[0], self.right_joystick[1])

        # 必须调用update同步状态
        self.device.update()

    def _set_button(self, target_btn: Any, pressed: bool) -> None:
        if pressed:
            self.device.press_button(target_btn)
        else:
            self.device.release_button(target_btn)
        self.device.update()

    def reset(self) -> None:
        try:
            self.init_device()
            self.device.reset()
            self.device.update()
        except Exception as e:
            logging.error(f'Failed to reset device: {str(e)}')
