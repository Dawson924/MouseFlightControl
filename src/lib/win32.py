import ctypes
from ctypes import wintypes
from typing import Callable, Optional

from PySide2.QtWidgets import QMessageBox, QWidget

from common.win32 import SPI_GETMOUSESPEED, SPI_SETMOUSESPEED


def set_mouse_speed(speed):
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)


def get_mouse_speed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0
    )
    return speed.value


def get_process_dpi_awareness():
    PROCESS_DPI_UNAWARE = 0
    PROCESS_SYSTEM_DPI_AWARE = 1
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    try:
        shcore = ctypes.WinDLL('shcore.dll', use_last_error=True)
        GetProcessDpiAwareness = shcore.GetProcessDpiAwareness
        GetProcessDpiAwareness.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ctypes.c_int),
        ]
        GetProcessDpiAwareness.restype = ctypes.HRESULT

        kernel32 = ctypes.WinDLL('kernel32.dll')
        hprocess = kernel32.GetCurrentProcess()

        awareness = ctypes.c_int()
        hr = GetProcessDpiAwareness(hprocess, ctypes.byref(awareness))
        if hr == 0:
            mode_names = {
                PROCESS_DPI_UNAWARE: 'PROCESS_DPI_UNAWARE (未感知)',
                PROCESS_SYSTEM_DPI_AWARE: 'PROCESS_SYSTEM_DPI_AWARE (系统感知)',
                PROCESS_PER_MONITOR_DPI_AWARE: 'PROCESS_PER_MONITOR_DPI_AWARE (每显示器感知)',
            }
            return awareness.value, mode_names.get(
                awareness.value, f'未知模式({awareness.value})'
            )
        else:
            return None, f'获取失败，错误码：{hr}'
    except Exception as e:
        return None, f'异常：{str(e)}'


def set_process_dpi_awareness(mode):
    try:
        shcore = ctypes.WinDLL('shcore.dll', use_last_error=True)
        SetProcessDpiAwareness = shcore.SetProcessDpiAwareness
        SetProcessDpiAwareness.argtypes = [ctypes.c_int]
        SetProcessDpiAwareness.restype = ctypes.HRESULT

        hr = SetProcessDpiAwareness(mode)
        if hr == 0:
            return True, '设置成功'
        else:
            error_code = ctypes.get_last_error()
            return False, f'错误码：{hr}, 系统错误码：{error_code}'
    except Exception as e:
        return False, f'异常：{str(e)}'


class MessageBox:
    def __init__(self, parent: Optional[QWidget] = None):
        self.parent = parent

    def set_parent(self, parent: QWidget):
        self.parent = parent

    def info(
        self,
        title: str = 'INFO',
        text: str = '',
        detail: str = '',
        buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
        default_button: QMessageBox.StandardButton = QMessageBox.Ok,
    ) -> QMessageBox.StandardButton:
        return self._create_msgbox(
            icon=QMessageBox.Information,
            title=title,
            text=text,
            detail=detail,
            buttons=buttons,
            default_button=default_button,
        )

    def warning(
        self,
        title: str = 'WARNING',
        text: str = '',
        detail: str = '',
        buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
        default_button: QMessageBox.StandardButton = QMessageBox.Ok,
    ) -> QMessageBox.StandardButton:
        return self._create_msgbox(
            icon=QMessageBox.Warning,
            title=title,
            text=text,
            detail=detail,
            buttons=buttons,
            default_button=default_button,
        )

    def error(
        self,
        title: str = 'ERROR',
        text: str = '',
        detail: str = '',
        buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
        default_button: QMessageBox.StandardButton = QMessageBox.Ok,
    ) -> QMessageBox.StandardButton:
        return self._create_msgbox(
            icon=QMessageBox.Critical,
            title=title,
            text=text,
            detail=detail,
            buttons=buttons,
            default_button=default_button,
        )

    def question(
        self,
        title: str = 'CONFIRM',
        text: str = '',
        detail: str = '',
        buttons: QMessageBox.StandardButtons = QMessageBox.Yes | QMessageBox.No,
        default_button: QMessageBox.StandardButton = QMessageBox.Yes,
    ) -> QMessageBox.StandardButton:
        return self._create_msgbox(
            icon=QMessageBox.Question,
            title=title,
            text=text,
            detail=detail,
            buttons=buttons,
            default_button=default_button,
        )

    def custom(
        self,
        icon: QMessageBox.Icon,
        title: str,
        text: str,
        detail: str = '',
        buttons: QMessageBox.StandardButtons = QMessageBox.Ok,
        default_button: QMessageBox.StandardButton = QMessageBox.Ok,
        callback: Optional[Callable[[QMessageBox.StandardButton], None]] = None,
    ) -> QMessageBox.StandardButton:
        result = self._create_msgbox(
            icon=icon,
            title=title,
            text=text,
            detail=detail,
            buttons=buttons,
            default_button=default_button,
        )
        if callback:
            callback(result)
        return result

    def _create_msgbox(
        self,
        icon: QMessageBox.Icon,
        title: str,
        text: str,
        detail: str,
        buttons: QMessageBox.StandardButtons,
        default_button: QMessageBox.StandardButton,
    ) -> QMessageBox.StandardButton:
        msg_box = QMessageBox(self.parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)

        if detail:
            msg_box.setDetailedText(detail)

        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(default_button)

        result = msg_box.exec_()
        return result
