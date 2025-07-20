import configparser
import os
import sys
import threading
import time
import ctypes
import pyvjoy
import win32api
import win32con
import pywintypes
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QPixmap, QCursor
from PySide2.QtWidgets import QApplication
from app import App
from input import InputStateMonitor
from ui.MainWindow import Ui_MainWindow
from ui.CursorOverhaul import CursorOverhaul
from ui.InterfaceOverlay import InterfaceOverlay  # 确保这个UI文件已正确生成

# 初始化vJoy设备
vjoy_device = None
# Windows API常量
SPI_SETMOUSESPEED = 113
SPI_GETMOUSESPEED = 112
MOUSE_SPEED_DEFAULT = 10  # Windows默认灵敏度(1-20)
# 全局配置文件名
CONFIG_FILE = "config.ini"

# 验证vJoy
try:
    vjoy_device = pyvjoy.VJoyDevice(1)
except Exception as e:
    app = QtWidgets.QApplication(sys.argv)
    error_msg = QtWidgets.QMessageBox()
    error_msg.setIcon(QtWidgets.QMessageBox.Critical)
    error_msg.setText("Failed to initialize vJoy Device")
    error_msg.setInformativeText("Please verify the installation of vJoy and make sure you enable it.\n" + str(e))
    error_msg.setWindowTitle("DEVICE NOT FOUND")
    error_msg.exec_()
    sys.exit(1)

class vjoyAxis():
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class vjoyState():
    def __init__(self, stick):
        self.stick = stick

class vjoySensitive():
    def __init__(self, mou, x, y):
        self.mou = mou
        self.x, self.y = x, y


# 全局控制变量
enabled = False
stop_thread = False  # 控制子线程退出
mouse_speed = 5  # 可通过UI设置的鼠标速度

# 全局变量初始化
original_mouse_speed = MOUSE_SPEED_DEFAULT
axis_max = 32767
axis_min = -axis_max
center_axis_x = 0
center_axis_y = 0

Axis = vjoyAxis(0, 0, 0)
State = vjoyState(False)
Sens = vjoySensitive(15.0, 0.7, 0.9)

screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)
screen_center_x = screen_width / 2
screen_center_y = screen_height / 2

# 输入状态跟踪
delta_x = 0
delta_y = 0
wheel_delta = 0
mouse_buttons = {"left": False, "right": False, "middle": False}
key_states = {Key.shift_r: False, Key.alt_r: False, Key.ctrl_r: False}


def reset_axis_pos():
    global Axis
    if Axis.x != center_axis_y:
        Axis.x = 0
    if Axis.y != center_axis_y:
        Axis.y = 0

def check_overflow(a, min_val, max_val):
    if a < min_val:
        return min_val
    elif a > max_val:
        return max_val
    return a

def wheel_th(sens_mo, sens_th, wheel_delta):
    return wheel_delta * 20 * sens_mo * sens_th

def get_mouse_position():
    try:
        return win32api.GetCursorPos()
    except pywintypes.error as e:
        # 处理访问被拒绝的情况
        if e.winerror == 5:  # Access is denied
            # 返回上次已知位置
            return (screen_center_x, screen_center_y)
        else:
            raise  # 重新抛出其他异常

def set_mouse_position(x, y):
    try:
        win32api.SetCursorPos((int(x), int(y)))
    except pywintypes.error as e:
        # 忽略设置光标位置时的错误
        pass

def set_mouse_speed(speed):
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)

def get_mouse_speed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0)
    return speed.value


# 窗口类
class MainWindow(QtWidgets.QMainWindow):
    pointer_signal = QtCore.Signal(bool)
    interface_signal = QtCore.Signal(str, int, str)

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("MouseFlightControl"))

        self.main_thread = None
        self.running = False
        self.language = 'en_US'
        self.key_toggle_enabled = '`'
        self.key_center = 'RB'
        self.opt_cursor_overhaul = False
        self.opt_interface_overlay = False

        self.ui.startBtn.clicked.connect(self.onButtonClick)
        self.ui.mouseSpeedSlider.valueChanged.connect(self.on_speed_changed)
        self.ui.mouseSpeedSlider.setRange(1, 10)
        self.ui.mouseSpeedSlider.setValue(5)
        self.ui.toggleEnabledKey.textChanged.connect(lambda text: setattr(self, 'key_toggle_enabled', text))
        self.ui.centerControlKey.textChanged.connect(lambda text: setattr(self, 'key_center', text))
        self.ui.cursorOverhaulOption.stateChanged.connect(lambda state: setattr(self, 'opt_cursor_overhaul', bool(state)))
        self.ui.interfaceOverlayOption.stateChanged.connect(lambda state: setattr(self, 'opt_interface_overlay', bool(state)))

        # 加载配置
        self.load_config()

        self.create_language_menu()
        self.retranslate_ui()

        self.show()

        # 创建界面覆盖信号
        self.interface = InterfaceOverlay()
        self.interface_signal.connect(self.interface.show_message)
        # 创建指针覆盖信号
        self.pointer = CursorOverhaul('assets/cursor.png')
        self.pointer_signal.connect(self.pointer.show_cursor)

    def load_default(self):
        self.ui.mouseSpeedSlider.setValue(5)

    def load_config(self):
        """从配置文件加载设置"""
        config = configparser.ConfigParser()

        # 如果配置文件存在，则加载
        if os.path.exists(CONFIG_FILE):
            try:
                config.read(CONFIG_FILE)

                if config.has_option('General', 'language'):
                    lang = config.get('General', 'language')
                    self.language = lang
                    translator = QtCore.QTranslator()
                    if translator.load(f"locales/{lang}.qm"):
                        QtWidgets.QApplication.instance().installTranslator(translator)
                        QtWidgets.QApplication.instance().translators.append(translator)

                if config.has_option('Controls', 'mouse_speed'):
                    speed = config.getint('Controls', 'mouse_speed')
                    self.ui.mouseSpeedSlider.setValue(speed)

                if config.has_option('Controls', 'key_toggle_enabled'):
                    key = config.get('Controls', 'key_toggle_enabled')
                    if len(key) == 1:
                        self.key_toggle_enabled = key

                if config.has_option('Controls', 'key_center'):
                    key = config.get('Controls', 'key_center')
                    if len(key) == 1:
                        self.key_center = key

                if config.has_option('Controls', 'opt_cursor_overhaul'):
                    key = config.getboolean('Controls', 'opt_cursor_overhaul')
                    self.opt_cursor_overhaul = key

                if config.has_option('Controls', 'opt_interface_overlay'):
                    key = config.getboolean('Controls', 'opt_interface_overlay')
                    self.opt_interface_overlay = key

            except Exception as e:
                print(f"加载配置时出错: {str(e)}")
                self.load_default()
        else:
            self.load_default()

    def save_config(self):
        """保存配置到文件"""
        config = configparser.ConfigParser()
        sections = ['General', 'Controls']

        # 添加设置部分
        config.add_section(sections[0])
        config.set(sections[0], 'language', self.language)

        config.add_section(sections[1])
        config.set(sections[1], 'mouse_speed', str(self.ui.mouseSpeedSlider.value()))
        config.set(sections[1], 'key_toggle_enabled', self.key_toggle_enabled)
        config.set(sections[1], 'key_center', self.key_center)
        config.set(sections[1], 'opt_cursor_overhaul', str(self.opt_cursor_overhaul))
        config.set(sections[1], 'opt_interface_overlay', str(self.opt_interface_overlay))

        # 写入配置文件
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def create_language_menu(self):
        """创建语言选择菜单"""
        self.language_menu = self.menuBar().addMenu("language")

        # 添加语言选项
        self.language_group = QtWidgets.QActionGroup(self)
        self.language_group.setExclusive(True)

        # 简体中文
        chinese_action = QtWidgets.QAction("简体中文", self)
        chinese_action.setCheckable(True)
        chinese_action.triggered.connect(lambda: self.change_language('zh_CN'))
        self.language_group.addAction(chinese_action)
        self.language_menu.addAction(chinese_action)

        # 英语
        english_action = QtWidgets.QAction("English", self)
        english_action.setCheckable(True)
        english_action.triggered.connect(lambda: self.change_language('en_US'))
        self.language_group.addAction(english_action)
        self.language_menu.addAction(english_action)

    def change_language(self, language_code):
        """更改应用程序语言"""
        for translator in QtWidgets.QApplication.instance().translators:
            QtWidgets.QApplication.instance().removeTranslator(translator)

        translator = QtCore.QTranslator()
        if translator.load(f"locales/{language_code}.qm"):
            QtWidgets.QApplication.instance().installTranslator(translator)
            QtWidgets.QApplication.instance().translators.append(translator)

        self.language = language_code

        # 重新翻译UI
        self.retranslate_ui()

    def retranslate_ui(self):
        """重新翻译UI文本"""
        # 窗口标题
        self.setWindowTitle(self.tr('MouseFlightControl'))
        self.language_menu.setTitle(self.tr("Language"))

        # 按钮文本
        self.ui.startBtn.setText(self.tr("Start") if not self.running else self.tr("Stop"))

        # 标签文本
        self.ui.titleLabel.setText(self.tr("Title"))
        self.ui.statusLabel.setText(self.tr("StatusStopped") if not self.running else self.tr("StatusWorking"))
        self.ui.speedLabel.setText(self.tr('Sensitive'))
        self.ui.speedValueLabel.setText(self.tr("CurrentValue") + f': {str(self.ui.mouseSpeedSlider.value())}')
        self.ui.toggleEnabledLabel.setText(self.tr("ToggleEnabled"))
        self.ui.toggleEnabledKey.setText(self.key_toggle_enabled)
        self.ui.centerControlLabel.setText(self.tr("CenterControl"))
        self.ui.centerControlKey.setText(self.key_center)
        self.ui.cursorOverhaulLabel.setText(self.tr("CursorOverhaul"))
        self.ui.cursorOverhaulOption.setChecked(self.opt_cursor_overhaul)
        self.ui.interfaceOverlayLabel.setText(self.tr("InterfaceOverlay"))
        self.ui.interfaceOverlayOption.setChecked(self.opt_interface_overlay)

    def on_speed_changed(self, value):
        """滑块值变化时, 更新状态与UI显示"""
        if self.running:
            return

        global mouse_speed
        mouse_speed = value
        self.ui.speedValueLabel.setText(f'{self.tr("CurrentValue")}: {str(self.ui.mouseSpeedSlider.value())}')
        if self.running:
            set_mouse_speed(value)

    def onButtonClick(self):
        """切换启用/禁用状态, 同步UI与子线程"""
        global enabled, stop_thread

        if not self.running:
            # 启动逻辑
            self.running = True
            self.toggle_enabled(True)
            self.start_main_thread()
        else:
            # 停止逻辑
            self.running = False
            self.toggle_enabled(False)
            self.stop_main_thread()

    def start_main_thread(self):
        """启动子线程"""
        global stop_thread
        stop_thread = False

        if self.main_thread and self.main_thread.is_alive():
            return

        self.ui.startBtn.setText(self.tr('Stop'))
        self.ui.statusLabel.setText(self.tr('StatusWorking'))
        self.ui.mouseSpeedSlider.setDisabled(True)
        self.ui.toggleEnabledKey.setDisabled(True)
        self.ui.centerControlKey.setDisabled(True)
        self.ui.cursorOverhaulOption.setDisabled(True)
        self.ui.interfaceOverlayOption.setDisabled(True)

        self.main_thread = threading.Thread(
            target=self.main,
            daemon=True
        )
        self.main_thread.start()

    def stop_main_thread(self):
        """暂停子线程"""
        global stop_thread
        stop_thread = True

        if self.main_thread and self.main_thread.is_alive():
            self.main_thread.join(timeout=1)

        self.ui.startBtn.setText(self.tr('Start'))
        self.ui.statusLabel.setText(self.tr('StatusStopped'))
        self.ui.mouseSpeedSlider.setDisabled(False)
        self.ui.toggleEnabledKey.setDisabled(False)
        self.ui.centerControlKey.setDisabled(False)
        self.ui.cursorOverhaulOption.setDisabled(False)
        self.ui.interfaceOverlayOption.setDisabled(False)
        self.main_thread = None
        vjoy_device.reset()
        self.pointer_signal.emit(False)

    def closeEvent(self, event):
        """停止子线程"""
        global stop_thread
        stop_thread = True

        if self.main_thread:
            self.main_thread.join()

        self.save_config()

        event.accept()

    def toggle_enabled(self, flag):
        if not self.running:
            return

        global enabled, original_mouse_speed, State

        enabled = flag
        State.stick = flag
        State.th = flag
        State.mouselock = flag
        State.btn = flag

        if flag:
            # 保存原始灵敏度并设置为UI指定值
            original_mouse_speed = get_mouse_speed()
            set_mouse_speed(mouse_speed)
            reset_axis_pos()
            if self.opt_cursor_overhaul: self.pointer_signal.emit(True)
            if self.opt_interface_overlay: self.interface_signal.emit("Controlled", 1000, 'green')
        else:
            # 恢复原始灵敏度
            set_mouse_speed(original_mouse_speed)
            self.interface_signal.emit("No control", 1000, 'red')
            self.pointer_signal.emit(False)

    def main(self):
        global delta_x, delta_y, wheel_delta, enabled
        try:
            input_state = InputStateMonitor()
            # 初始/上一次的按键状态
            toggle_key_prev = False
            center_key_prev = False

            prev_x, prev_y = screen_center_x, screen_center_y

            while not stop_thread:  # 用stop_thread控制退出
                input_state.update()
                # 当前的按键状态
                toggle_key_current = input_state.is_pressed(self.key_toggle_enabled)
                center_key_current = input_state.is_pressed(self.key_center)

                # 状态从curr流向prev，在中间计算delta
                curr_x, curr_y = get_mouse_position()
                delta_x = curr_x - prev_x
                delta_y = curr_y - prev_y
                prev_x, prev_y = curr_x, curr_y

                if toggle_key_current and not toggle_key_prev:
                    self.toggle_enabled(not enabled)

                if enabled and center_key_current and not center_key_prev:
                    set_mouse_position(screen_center_x, screen_center_y)

                # 更新上一次的按键状态
                toggle_key_prev = toggle_key_current
                center_key_prev = center_key_current

                if enabled and State.stick:
                    Axis.x += delta_x * Sens.x * Sens.mou * 0.48
                    Axis.y += delta_y * Sens.y * Sens.mou

                    x_percent = (Axis.x / axis_max) * 100
                    y_percent = (Axis.y / axis_max) * 100
                    screen_x = screen_center_x + (x_percent / 100) * (screen_width / 2)
                    screen_y = screen_center_y + (y_percent / 100) * (screen_height / 2)
                    prev_x, prev_y = screen_x, screen_y

                    Axis.x = check_overflow(Axis.x, axis_min, axis_max)
                    Axis.y = check_overflow(Axis.y, axis_min, axis_max)
                    # Axis.th_l = check_overflow(Axis.th_l, axis_min, axis_max)
                    # Axis.th_r = check_overflow(Axis.th_r, axis_min, axis_max)

                    def map_to_vjoy(val):
                        return int((val - axis_min) / (axis_max - axis_min) * 32767) + 1

                    vjoy_device.set_axis(pyvjoy.HID_USAGE_X, map_to_vjoy(Axis.x))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_Y, map_to_vjoy(Axis.y))
                    # vjoy_device.set_axis(pyvjoy.HID_USAGE_SL0, map_to_vjoy(Axis.th_l))
                    # vjoy_device.set_axis(pyvjoy.HID_USAGE_SL1, map_to_vjoy(Axis.th_r))

                wheel_delta = 0
                time.sleep(0.016)

        except KeyboardInterrupt:
            pass
        finally:
            set_mouse_speed(original_mouse_speed)
            vjoy_device.reset()


if __name__ == "__main__":
    app = App(sys.argv)

    # 检查本地化文件夹是否存在
    if not os.path.exists('locales'):
        error_msg = QtWidgets.QMessageBox()
        error_msg.setIcon(QtWidgets.QMessageBox.Critical)
        error_msg.setText("Missing locale files")
        error_msg.setInformativeText("Cannot find 'locales' directory. Please verify the program's files are installed correctly.")
        error_msg.setWindowTitle("PATH NOT FOUND")
        error_msg.exec_()
        sys.exit(1)

    translator = QtCore.QTranslator()
    if translator.load(f"locales/en_US.qm"):
        app.installTranslator(translator)
        app.translators.append(translator)

    window = MainWindow()

    global instance
    instance = window

    sys.exit(app.exec_())
