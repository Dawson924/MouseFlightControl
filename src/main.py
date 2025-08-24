import configparser
import os
import sys
import threading
import time
import ctypes
from types import SimpleNamespace
import pyvjoy
import win32api

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from app import App
from controller.base import BaseController
from controller.control import FixedWingController, HelicopterController
from controller.manager import ControllerManager
from enums.widget import OptionWidget
from input import InputStateMonitor
from ui.MainWindow import Ui_MainWindow
from ui.overlay.CursorGraph import CursorGraph
from ui.overlay.HintLabel import HintLabel

from calc import map_to_vjoy
from ui.overlay.IndicatorWindow import IndicatorWindow
from utils import check_overflow, wheel_step

# 初始化vJoy设备
vjoy_device = None
try:
    vjoy_device = pyvjoy.VJoyDevice(1)
    vjoy_device.set_axis(pyvjoy.HID_USAGE_Z, 0x8000)
    vjoy_device.set_axis(pyvjoy.HID_USAGE_RZ, 0x4000)
except Exception as e:
    app = QtWidgets.QApplication(sys.argv)
    error_msg = QtWidgets.QMessageBox()
    error_msg.setIcon(QtWidgets.QMessageBox.Critical)
    error_msg.setText("Failed to initialize vJoy Device")
    error_msg.setInformativeText(f'{str(e)}\n')
    error_msg.setWindowTitle("Error")
    error_msg.exec_()
    sys.exit(1)

# Windows API常量
SPI_SETMOUSESPEED = 113
SPI_GETMOUSESPEED = 112
MOUSE_SPEED_DEFAULT = 10  # Windows默认灵敏度(1-20)

# 配置选项存储
CONFIG_FILE = "config.ini"
CONFIG = {
    'General': {
        'language': (str),
        'show_tips': (bool),
    },
    'Controls': {
        'mouse_speed': (int),
        'controller': (int),
        'key_toggle': (str),
        'key_center': (str),
        'key_freelook': (str),
        'key_view_center': (str),
        'camera_fov': (int),
        'key_taxi': (str),
    },
    'Options': {
        'show_cursor': (bool),
        'hint_overlay': (bool),
        'show_indicator': (bool),
        'button_mapping': (bool),
        'memorize_axis_pos': (bool),
        'freelook_auto_center': (bool),
    },
    'Internal': {
        'w_size': (int),
        'min_w_size': (int),
        'max_w_size': (int),
        'report_rate': (float),
        'retry_count': (int),
    },
    'External': {}
}

# 控制器管理
controllers = ControllerManager()

class vjoyAxis():
    def __init__(self, x, y, th, rd):
        self.x, self.y, self.th, self.rd = x, y, th, rd
        self.vx, self.vy, self.vz = 0, 0, 0

class vjoyState():
    def __init__(self, stick, th):
        self.stick = stick
        self.th = th

class vjoySensitive():
    def __init__(self, mou, x, y, th):
        self.mou = mou
        self.x, self.y = x, y
        self.th = th


# 全局控制变量
enabled = False
taxi_mode = False
stop_thread = False  # 控制子线程退出

# 全局变量初始化
axis_max = 32767
axis_min = -axis_max
center_axis_x = 0
center_axis_y = 0
axis_step = int(axis_max * 2 / 120)

Axis = vjoyAxis(0, 0, axis_max, 0)
Sens = vjoySensitive(15.0, 0.7, 0.9, 1.9)

screen_width = win32api.GetSystemMetrics(0)
screen_height = win32api.GetSystemMetrics(1)
screen_center_x = screen_width / 2
screen_center_y = screen_height / 2

# 输入状态跟踪
delta_x = 0
delta_y = 0

def set_mouse_speed(speed):
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETMOUSESPEED, 0, speed, 0)

def get_mouse_speed():
    speed = ctypes.c_int()
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0)
    return speed.value


class MainWindow(QtWidgets.QMainWindow):
    dynamic_widgets = {}
    pointer_show = QtCore.Signal(bool)
    interface_show = QtCore.Signal(str, int, str)
    indicator_show = QtCore.Signal(bool)
    indicator_update = QtCore.Signal(float, float, float, float)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.w_size = 350
        self.min_w_size = 300
        self.max_w_size = 500
        self.setup_ui()

        # 程序状态
        self.main_thread = None
        self.running = False
        self.original_mouse_speed = get_mouse_speed()
        self.report_rate = 0.004
        self.retry_count = 2

        # 配置默认值
        self.language = 'en_US'
        self.show_tips = True
        self.mouse_speed = 5
        self.key_toggle = '`'
        self.key_center = 'MMB'
        self.key_freelook = 'tab'
        self.key_view_center = 'capslock'
        self.camera_fov = 90
        self.key_taxi = 'alt + `'
        self.controller = 0
        self.show_cursor = False
        self.hint_overlay = True
        self.show_indicator = False
        self.button_mapping = True
        self.memorize_axis_pos = True
        self.freelook_auto_center = False
        self.__external__ = SimpleNamespace()

        # 加载所有配置
        self.load_config()

        # 加载配置的语言
        translator = QtCore.QTranslator()
        if translator.load(f"locales/{self.language}.qm"):
            QtWidgets.QApplication.instance().installTranslator(translator)
            QtWidgets.QApplication.instance().translators.append(translator)

        self.create_menu()

        self.setup_controllers()
        self.create_controller_widgets(self.controller)

        self.retranslate_ui()
        self.update_ui_state()

        # 用户页面操作
        self.ui.startBtn.clicked.connect(self.on_button_click)
        self.ui.mouseSpeedSlider.valueChanged.connect(self.on_speed_changed)
        self.ui.mouseSpeedSlider.setRange(1, 20)
        self.ui.mouseSpeedSlider.setValue(self.mouse_speed)
        self.ui.toggleEnabledKey.textChanged.connect(lambda text: self.update('key_toggle', text))
        self.ui.centerControlKey.textChanged.connect(lambda text: self.update('key_center', text))
        self.ui.enableFreelookKey.textChanged.connect(lambda text: self.update('key_freelook', text))
        self.ui.viewCenterKey.textChanged.connect(lambda text: self.update('key_view_center', text))
        self.ui.cameraFovSpinBox.valueChanged.connect(lambda value: self.update('camera_fov', value))
        self.ui.taxiModeKey.textChanged.connect(lambda text: self.update('key_taxi', text))
        self.ui.controllerComboBox.currentIndexChanged.connect(self.on_controller_changed)
        self.ui.showCursorOption.stateChanged.connect(lambda state: self.update('show_cursor', bool(state)))
        self.ui.hintOverlayOption.stateChanged.connect(lambda state: self.update('hint_overlay', bool(state)))
        self.ui.showIndicatorOption.stateChanged.connect(lambda state: self.update('show_indicator', bool(state)))
        self.ui.buttonMappingOption.stateChanged.connect(lambda state: self.update('button_mapping', bool(state)))
        self.ui.memorizeAxisPosOption.stateChanged.connect(lambda state: self.update('memorize_axis_pos', bool(state)))
        self.ui.freelookAutoCenterOption.stateChanged.connect(lambda state: self.update('freelook_auto_center', bool(state)))

        # 创建界面绘制信号
        self.interface = HintLabel()
        self.interface_show.connect(self.interface.show_message)
        self.pointer = CursorGraph()
        self.pointer_show.connect(self.pointer.show_cursor)
        self.indicator = IndicatorWindow()
        self.indicator_show.connect(self.indicator.show_overlay)
        self.indicator_update.connect(self.update_indicator)

        self.show()

    def setup_ui(self):
        self.ui.setupUi(self)
        self.setWindowFlags(self.windowFlags() &
                            ~Qt.WindowMaximizeButtonHint)
        self.setMinimumWidth(self.min_w_size)
        self.setMaximumWidth(self.max_w_size)

    def setup_controllers(self):
        controllers.register(0, None, { 'name': 'None' })
        controllers.register(1, FixedWingController, {
            'name': self.tr('FixedWingMode'),
            'options': {
                ('plane_step', OptionWidget.SpinBox, 3000)
            },
            'i18n': {
                'en_US': {
                    'plane_step': 'Step (per frame)',
                },
                'zh_CN': {
                    'plane_step': '每次滚轮滚动',
                },
                'ru_RU': {
                    'plane_step': 'Шаг (на кадр)'
                }
            }
        })
        controllers.register(2, HelicopterController, {
            'name': self.tr('HelicopterMode'),
            'options': {
                ('heli_step', OptionWidget.SpinBox, 150)
            },
            'i18n': {
                'en_US': {
                    'heli_step': 'Step (per frame)',
                },
                'zh_CN': {
                    'heli_step': '每帧键盘移动',
                },
                'ru_RU': {
                    'heli_step': 'Шаг (на кадр)'
                }
            }
        })
        index = self.controller
        self.ui.controllerComboBox.clear()
        for name in controllers.names():
            self.ui.controllerComboBox.addItem(name)
        self.ui.controllerComboBox.setCurrentIndex(index)

    def create_controller_widgets(self, id):
        """根据控制器元数据创建动态控件"""
        # 清除现有的动态控件
        self.clear_controller_widgets()

        # 获取控制器元数据
        metadata = controllers.get_metadata(id)
        if not metadata or 'options' not in metadata:
            return

        # 为每个选项创建控件
        for (option, widget, default) in metadata['options']:
            # 创建水平布局
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.setSpacing(10)  # 设置间距为10
            h_layout.setContentsMargins(0, 0, 0, 0)

            # 创建标签
            text = metadata['i18n'][self.language][option]
            label = QtWidgets.QLabel(text)
            label.setObjectName(f"{option}Label")
            label.setMinimumWidth(150)
            h_layout.addWidget(label)

            # 添加水平弹簧
            spacer = QtWidgets.QSpacerItem(40, 20,
                                        QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Minimum)
            h_layout.addItem(spacer)

            if widget == OptionWidget.CheckBox:
                # 创建复选框
                checkbox = QtWidgets.QCheckBox()
                checkbox.setObjectName(f"{option}Option")
                if hasattr(self.__external__, option):
                    value = getattr(self.__external__, option)
                    if isinstance(value, str):
                        if value.lower() == 'true':
                            value = True
                        elif value.lower() == 'false':
                            value = False
                        else:
                            value = False
                    checkbox.setChecked(bool(value))
                else:
                    setattr(self.__external__, option, default)
                    checkbox.setChecked(default)

                checkbox.stateChanged.connect(
                    lambda state, opt=option: setattr(self.__external__, opt, bool(state))
                )
                h_layout.addWidget(checkbox)

                self.dynamic_widgets[option] = {
                    'label': label,
                    'checkbox': checkbox,
                    'layout': h_layout
                }

            elif widget == OptionWidget.LineEdit:
                # 创建文本输入
                line_edit = QtWidgets.QLineEdit()
                line_edit.setObjectName(f"{option}Option")
                line_edit.setFixedWidth(100)  # 设置固定宽度

                # 从配置或默认值获取当前值
                if hasattr(self.__external__, option):
                    value = getattr(self.__external__, option)
                else:
                    value = default
                    setattr(self.__external__, option, value)

                # 设置验证器根据值的类型
                if isinstance(value, int):
                    line_edit.setValidator(QtGui.QIntValidator())
                elif isinstance(value, float):
                    line_edit.setValidator(QtGui.QDoubleValidator())

                line_edit.setText(str(value))

                line_edit.textChanged.connect(
                    lambda text, opt=option: setattr(self.__external__, opt, str(text))
                )

                h_layout.addWidget(line_edit)

                self.dynamic_widgets[option] = {
                    'label': label,
                    'line_edit': line_edit,
                    'layout': h_layout
                }

            elif widget == OptionWidget.SpinBox:
                # 创建数值选择器
                spin_box = QtWidgets.QSpinBox()
                spin_box.setObjectName(f"{option}Option")
                spin_box.setFixedWidth(100)
                spin_box.setMinimum(0)
                spin_box.setMaximum(1000000)

                if hasattr(self.__external__, option):
                    value = getattr(self.__external__, option)
                    try:
                        value = int(value)
                    except ValueError:
                        value = default
                else:
                    value = default
                    setattr(self.__external__, option, value)

                spin_box.setValue(value)

                spin_box.valueChanged.connect(
                    lambda value, opt=option: setattr(self.__external__, opt, value))

                h_layout.addWidget(spin_box)

                self.dynamic_widgets[option] = {
                    'label': label,
                    'spin_box': spin_box,
                    'layout': h_layout
                }

            # 添加到布局
            self.ui.ControllerVerticalLayout.addLayout(h_layout)

    def clear_controller_widgets(self):
        """清除所有动态控件"""
        while self.ui.ControllerVerticalLayout.count():
            item = self.ui.ControllerVerticalLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.delete_layout(item.layout())

        self.dynamic_widgets = {}

    def delete_layout(self, layout):
        """递归删除布局中的所有控件"""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.delete_layout(item.layout())

        # 删除布局本身
        layout.deleteLater()

    def load_config(self):
        """从配置文件加载设置"""
        config = configparser.ConfigParser()

        if os.path.exists(CONFIG_FILE):
            try:
                config.read(CONFIG_FILE)
                for section, options in CONFIG.items():
                    if config.has_section(section):
                        if section == 'External':
                            for k, v in config.items('External'):
                                if v.lower() == 'true':
                                    setattr(self.__external__, k, True)
                                elif v.lower() == 'false':
                                    setattr(self.__external__, k, False)
                                elif v.isdigit():
                                    setattr(self.__external__, k, int(v))
                                else:
                                    setattr(self.__external__, k, v)
                        else:
                            for option, (converter) in options.items():
                                if config.has_option(section, option):
                                    if converter is bool:
                                        value = config.getboolean(section, option)
                                    elif converter is int:
                                        value = config.getint(section, option)
                                    elif converter is float:
                                        value = config.getfloat(section, option)
                                    else:
                                        value = config.get(section, option)

                                    self._set_attr_value(option, value)
                return True
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        return False

    def save_config(self):
        """保存配置到文件"""
        config = configparser.ConfigParser()

        for section, options in CONFIG.items():
            config.add_section(section)

            if section == 'External':
                for k, v in self.__external__.__dict__.items():
                    config.set(section, k, str(v))
            else:
                for option in options.keys():
                    value = self._get_attr_value(option)
                    config.set(section, option, str(value))

        try:
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
            print("配置文件保存成功")
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def _get_attr_value(self, attr_path):
        parts = attr_path.split('.')
        obj = self
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return None
        return obj

    def _set_attr_value(self, attr_path, value):
        parts = attr_path.split('.')
        obj = self
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return
        last_part = parts[-1]
        if hasattr(obj, last_part):
            setattr(obj, last_part, value)

    def create_menu(self):
        self.general_menu = self.menuBar().addMenu('')
        self.language_menu = self.menuBar().addMenu('')

        self.tip_action = QtWidgets.QAction('', self)
        self.tip_action.setCheckable(True)
        self.tip_action.setChecked(self.show_tips)
        self.tip_action.triggered.connect(lambda: self.update('show_tips', not self.show_tips))
        self.general_menu.addAction(self.tip_action)

        # 添加语言选项
        self.language_group = QtWidgets.QActionGroup(self)
        self.language_group.setExclusive(True)

        # 英语
        self.english_action = QtWidgets.QAction("English", self)
        self.english_action.setCheckable(True)
        self.english_action.triggered.connect(lambda: self.change_language('en_US'))
        self.language_group.addAction(self.english_action)
        self.language_menu.addAction(self.english_action)
        self.english_action.setChecked(self.language == 'en_US')

        # 简体中文
        self.chinese_action = QtWidgets.QAction("简体中文", self)
        self.chinese_action.setCheckable(True)
        self.chinese_action.triggered.connect(lambda: self.change_language('zh_CN'))
        self.language_group.addAction(self.chinese_action)
        self.language_menu.addAction(self.chinese_action)
        self.chinese_action.setChecked(self.language == 'zh_CN')

        # 俄语
        self.russian_action = QtWidgets.QAction("Русский", self)
        self.russian_action.setCheckable(True)
        self.russian_action.triggered.connect(lambda: self.change_language('ru_RU'))
        self.language_group.addAction(self.russian_action)
        self.language_menu.addAction(self.russian_action)
        self.russian_action.setChecked(self.language == 'ru_RU')

    def change_language(self, language_code):
        """更改应用程序语言"""
        for translator in QtWidgets.QApplication.instance().translators:
            QtWidgets.QApplication.instance().removeTranslator(translator)

        translator = QtCore.QTranslator()
        if translator.load(f"locales/{language_code}.qm"):
            QtWidgets.QApplication.instance().installTranslator(translator)
            QtWidgets.QApplication.instance().translators.append(translator)

        self.language = language_code
        self.retranslate_ui()
        self.setup_controllers()
        self.create_controller_widgets(self.controller)

    def retranslate_ui(self):
        """重新翻译UI文本"""
        # 窗口标题
        self.setWindowTitle(self.tr('Title'))
        self.general_menu.setTitle(self.tr("General"))
        self.language_menu.setTitle(self.tr("Language"))
        self.tip_action.setText(self.tr('ShowTips'))

        # 按钮文本
        self.ui.startBtn.setText(self.tr("Start") if not self.running else self.tr("Stop"))

        # 标签文本
        self.ui.controlsTitleLabel.setText(self.tr("ControlsTitle"))
        self.ui.statusLabel.setText(self.tr("StatusStopped") if not enabled else self.tr("StatusWorking"))
        self.ui.speedLabel.setText(self.tr('Sensitive'))
        self.ui.speedValueLabel.setText(self.tr("CurrentValue") + f': {str(self.ui.mouseSpeedSlider.value())}')
        self.ui.toggleEnabledLabel.setText(self.tr("ToggleEnabled"))
        self.ui.toggleEnabledKey.setText(self.key_toggle)
        self.ui.centerControlLabel.setText(self.tr("CenterControl"))
        self.ui.centerControlKey.setText(self.key_center)
        self.ui.enableFreelookLabel.setText(self.tr("EnableFreelook"))
        self.ui.enableFreelookKey.setText(self.key_freelook)
        self.ui.viewCenterLabel.setText(self.tr("ViewCenter"))
        self.ui.viewCenterKey.setText(self.key_view_center)
        self.ui.cameraFovLabel.setText(self.tr('CameraFov'))
        self.ui.cameraFovSpinBox.setValue(self.camera_fov)
        self.ui.taxiModeLabel.setText(self.tr('TaxiMode'))
        self.ui.taxiModeKey.setText(self.key_taxi)
        self.ui.controlModeDescription.setText(self.tr("ControlModeTip"))
        self.ui.controllerLabel.setText(self.tr("Controller"))
        self.ui.controllerComboBox.setCurrentIndex(self.controller)
        self.ui.controllerComboBox.setCurrentText(controllers.get_name(self.controller))
        self.ui.optionsTitleLabel.setText(self.tr("OptionsTitle"))
        self.ui.showCursorLabel.setText(self.tr("ShowCursor"))
        self.ui.showCursorOption.setChecked(self.show_cursor)
        self.ui.hintOverlayLabel.setText(self.tr("HintOverlay"))
        self.ui.hintOverlayOption.setChecked(self.hint_overlay)
        self.ui.showIndicatorLabel.setText(self.tr('ShowIndicator'))
        self.ui.showIndicatorOption.setChecked(self.show_indicator)
        self.ui.buttonMappingLabel.setText(self.tr("ButtonMapping"))
        self.ui.buttonMappingOption.setChecked(self.button_mapping)
        self.ui.memorizeAxisPosLabel.setText(self.tr("MemorizeAxisPos"))
        self.ui.memorizeAxisPosOption.setChecked(self.memorize_axis_pos)
        self.ui.freelookAutoCenterLabel.setText(self.tr('FreelookAutoCenter'))
        self.ui.freelookAutoCenterOption.setChecked(self.freelook_auto_center)

    def on_speed_changed(self, value):
        self.mouse_speed = value
        self.ui.speedValueLabel.setText(f'{self.tr("CurrentValue")}: {str(self.ui.mouseSpeedSlider.value())}')
        if self.running:
            set_mouse_speed(value)

    def on_controller_changed(self, value):
        self.controller = value
        self.create_controller_widgets(value)
        self.update_ui_state()

    def on_button_click(self):
        """切换启用/禁用状态, 同步UI与子线程"""
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

    def update(self, attr: str, value):
        self._set_attr_value(attr, value)
        self.update_ui_state()

    def update_ui_state(self):
        disabled = self.running
        self.ui.startBtn.setText(self.tr('Start') if not self.running else self.tr('Stop'))
        self.ui.statusLabel.setText(self.tr('StatusWorking') if disabled else self.tr('StatusStopped'))
        self.ui.mouseSpeedSlider.setDisabled(disabled)
        self.ui.toggleEnabledKey.setDisabled(disabled)
        self.ui.centerControlKey.setDisabled(disabled)
        self.ui.controllerComboBox.setDisabled(disabled)
        self.ui.enableFreelookKey.setDisabled(disabled)
        self.ui.viewCenterKey.setDisabled(disabled)
        self.ui.taxiModeKey.setDisabled(disabled)
        self.ui.controlModeDescription.setHidden(not self.show_tips)
        for option, controls in self.dynamic_widgets.items():
            if 'checkbox' in controls:
                controls['checkbox'].setDisabled(disabled)
            elif 'line_edit' in controls:
                controls['line_edit'].setDisabled(disabled)
            elif 'spin_box' in controls:
                controls['spin_box'].setDisabled(disabled)
        self.ui.showCursorOption.setDisabled(disabled)
        self.ui.hintOverlayOption.setDisabled(disabled)
        self.ui.showIndicatorOption.setDisabled(disabled)
        self.ui.buttonMappingOption.setDisabled(disabled)
        self.ui.memorizeAxisPosOption.setDisabled(disabled)
        self.ui.freelookAutoCenterOption.setDisabled(disabled)
        self.ui.cameraFovSpinBox.setDisabled(disabled)

        self.ui.verticalLayout.invalidate()
        self.ui.verticalLayout.activate()
        QtWidgets.QApplication.processEvents()
        self.setMinimumHeight(self.minimumSizeHint().height())
        self.resize(self.w_size, self.minimumSizeHint().height())

    def start_main_thread(self):
        """启动子线程"""
        global stop_thread
        stop_thread = False

        if self.main_thread and self.main_thread.is_alive():
            return

        self.update_ui_state()

        if self.show_indicator:
            self.indicator.show_overlay(True)

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

        self.update_ui_state()
        self.indicator.show_overlay(False)

        self.main_thread = None
        self.pointer_show.emit(False)

    def closeEvent(self, event):
        """停止子线程"""
        global stop_thread
        stop_thread = True

        if self.main_thread:
            self.main_thread.join()

        self.w_size = self.size().width()
        self.save_config()

        event.accept()

    def toggle_enabled(self, flag):
        if not self.running:
            return

        global enabled, taxi_mode
        enabled = flag

        if flag:
            set_mouse_speed(self.mouse_speed)
            if self.show_cursor: self.pointer_show.emit(True)
            if self.hint_overlay: self.interface_show.emit(self.tr('Controlled'), 1000, 'green')
        else:
            set_mouse_speed(self.original_mouse_speed)
            self.pointer_show.emit(False)
            if self.hint_overlay: self.interface_show.emit(self.tr('NoControl'), 1000, 'red')

        self.retranslate_ui()

    def main(self):
        global delta_x, delta_y, enabled, taxi_mode
        try:
            Class = controllers.get_class(self.controller)
            if Class:
                controller = Class(vjoy_device)
            else:
                controller = None

            input = InputStateMonitor(self.report_rate, self.retry_count)
            input.set_mouse_position(screen_center_x, screen_center_y)

            map_to_percentage = lambda value, rev=False: map_to_vjoy(int(value)) / 0x8000 if not rev else 1 - map_to_vjoy(int(value)) / 0x8000

            prev_x, prev_y = screen_center_x, screen_center_y
            stick_x, stick_y = screen_center_x, screen_center_y
            cam_x, cam_y = screen_center_x, screen_center_y
            freelook_on = False
            use_cache = False

            while not stop_thread:  # 用stop_thread控制退出
                input.update()

                if input.is_hotkey_pressed(self.key_toggle):
                    _flag = not enabled
                    self.toggle_enabled(_flag)
                    if self.memorize_axis_pos:
                        if not _flag:
                            stick_x, stick_y = prev_x, prev_y
                        elif stick_x is not None and stick_y is not None:
                            prev_x, prev_y = stick_x, stick_y
                            use_cache = True

                if input.is_hotkey_pressed(self.key_taxi):
                    if enabled:
                        taxi_mode = not taxi_mode
                        Axis.rd = 0
                        if taxi_mode:
                            if self.hint_overlay: self.interface_show.emit(self.tr('TaxiModeOn'), 1000, 'green')
                        else:
                            if self.hint_overlay: self.interface_show.emit(self.tr('TaxiModeOff'), 1000, 'red')

                if enabled and input.is_hotkey_pressed(self.key_center):
                    prev_x, prev_y = screen_center_x, screen_center_y
                    use_cache = True

                if enabled and input.is_hotkey_pressed(self.key_view_center):
                    Axis.vz = axis_min + self.camera_fov * axis_step
                    if not freelook_on:
                        Axis.vx, Axis.vy, cam_x, cam_y = 0, 0, screen_center_x, screen_center_y

                if enabled and self.button_mapping and not freelook_on:
                    if input.is_pressing('LMB'):
                        vjoy_device.set_button(1, True)
                    else:
                        vjoy_device.set_button(1, False)
                    if input.is_pressing('RMB'):
                        vjoy_device.set_button(2, True)
                    else:
                        vjoy_device.set_button(2, False)
                    if input.is_pressing('MMB'):
                        vjoy_device.set_button(3, True)
                    else:
                        vjoy_device.set_button(3, False)
                    if input.is_pressing('XMB1'):
                        vjoy_device.set_button(4, True)
                    else:
                        vjoy_device.set_button(4, False)
                    if input.is_pressing('XMB2'):
                        vjoy_device.set_button(5, True)
                    else:
                        vjoy_device.set_button(5, False)

                if enabled:
                    if input.is_pressed(self.key_freelook):
                        freelook_on = True
                        stick_x, stick_y = prev_x, prev_y
                        if self.freelook_auto_center:
                            Axis.vx, Axis.vy = 0, 0
                            prev_x, prev_y = screen_center_x, screen_center_y
                            use_cache = True
                        else:
                            prev_x, prev_y = cam_x, cam_y
                            use_cache = True
                    if input.is_released(self.key_freelook):
                        freelook_on = False
                        cam_x, cam_y = prev_x, prev_y
                        if self.freelook_auto_center:
                            Axis.vx, Axis.vy = 0, 0
                        prev_x, prev_y = stick_x, stick_y
                        use_cache = True

                    if use_cache:
                        input.set_mouse_position(prev_x, prev_y)
                        use_cache = False

                    curr_x, curr_y = input.get_mouse_position()
                    delta_x = curr_x - prev_x
                    delta_y = curr_y - prev_y
                    prev_x, prev_y = curr_x, curr_y

                    if input.is_pressing(self.key_freelook) and freelook_on:
                        Axis.vx += delta_x * Sens.x * Sens.mou * 0.48
                        Axis.vy += delta_y * Sens.y * Sens.mou

                        x_percent = (Axis.vx / axis_max) * 100
                        y_percent = (Axis.vy / axis_max) * 100
                        screen_x = screen_center_x + (x_percent / 100) * (screen_width / 2)
                        screen_y = screen_center_y + (y_percent / 100) * (screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        Axis.vx = check_overflow(Axis.vx, axis_min, axis_max)
                        Axis.vy = check_overflow(Axis.vy, axis_min, axis_max)

                        Axis.vz += wheel_step(axis_step * 10, -input.get_wheel_delta())
                        Axis.vz = check_overflow(Axis.vz, axis_min, axis_max)
                    else:
                        Axis.x += delta_x * Sens.x * Sens.mou * 0.48
                        Axis.y += delta_y * Sens.y * Sens.mou

                        x_percent = (Axis.x / axis_max) * 100
                        y_percent = (Axis.y / axis_max) * 100
                        screen_x = screen_center_x + (x_percent / 100) * (screen_width / 2)
                        screen_y = screen_center_y + (y_percent / 100) * (screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        Axis.x = check_overflow(Axis.x, axis_min, axis_max)
                        Axis.y = check_overflow(Axis.y, axis_min, axis_max)

                        if taxi_mode:
                            Axis.rd = Axis.x

                if enabled:
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_X, map_to_vjoy(int(Axis.x)))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_Y, map_to_vjoy(int(Axis.y)))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_Z, map_to_vjoy(int(Axis.th)))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_RZ, map_to_vjoy(int(Axis.rd)))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_RX, map_to_vjoy(int(Axis.vx)))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_RY, map_to_vjoy(int(Axis.vy)))
                    vjoy_device.set_axis(pyvjoy.HID_USAGE_SL0, map_to_vjoy(int(Axis.vz)))

                if controller is not None and isinstance(controller, BaseController):
                    controller.update(SimpleNamespace(
                        Axis=Axis,
                        axis_min=axis_min,
                        axis_max=axis_max,
                        vjoy=vjoy_device,
                        input=input,
                        options=self.__external__,
                        enabled=enabled,
                    ), self)

                if self.show_indicator:
                    x_val = map_to_percentage(Axis.x)
                    y_val = map_to_percentage(Axis.y)
                    throttle_val = map_to_percentage(Axis.th, True)
                    rudder_val = map_to_percentage(Axis.rd)
                    self.indicator_update.emit(x_val, y_val, throttle_val, rudder_val)

                input.reset_wheel_delta()

                time.sleep(self.report_rate)

        except KeyboardInterrupt:
            pass
        finally:
            set_mouse_speed(self.original_mouse_speed)
            vjoy_device.reset()

    def update_indicator(self, x, y, throttle, rudder):
        """在主线程中更新IndicatorWindow的显示"""
        self.indicator.set_xy_values(x, y)
        self.indicator.set_throttle_value(throttle)
        self.indicator.set_rudder_value(rudder)


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

    font = QFont("Arial", 9)
    app.setFont(font)

    window = MainWindow()

    sys.exit(app.exec_())
