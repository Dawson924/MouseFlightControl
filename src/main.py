import configparser
import ctypes
import os
import sys
import threading
import time
from types import SimpleNamespace
from typing import Dict

import psutil
from lupa import LuaRuntime
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import QCoreApplication, Qt
from PySide2.QtGui import QFont, QScreen

from app import App
from common.config import CONFIG, CONFIG_FILE
from common.constants import APP_VERSION, SCRIPT_INI_PATH
from controller.base import BaseController
from controller.control import FixedWingController, HelicopterController
from controller.manager import ControllerManager
from input import InputStateMonitor
from lib.config import load_config, save_config, validate_config
from lib.event import EventEmitter
from lib.fs import choose_single_file, open_directory
from lib.joystick import (
    AXIS_LENGTH,
    AXIS_MAX,
    AXIS_MIN,
    HID_RX,
    HID_RY,
    HID_RZ,
    HID_SLIDER,
    HID_X,
    HID_Y,
    HID_Z,
    get_joystick_device,
)
from lib.logger import get_logger, init_logger, logger
from lib.script import get_default
from lib.win32 import (
    MessageBox,
    get_mouse_speed,
    get_process_dpi_awareness,
    set_mouse_speed,
    set_process_dpi_awareness,
)
from script_engine.database import ScriptDatabase
from script_engine.runtime import load_lua_scripts
from type.script import ScriptModule
from type.widget import OptionWidget
from ui.MainWindow import Ui_MainWindow
from ui.overlay.CursorGraph import CursorGraph
from ui.overlay.HintLabel import HintLabel
from ui.overlay.IndicatorWindow import IndicatorWindow
from ui.window.ScriptWindow import ScriptWindow
from utils import axis2fov, check_overflow, fov, wheel_step

# 控制器管理
controllers = ControllerManager()


class AxisPos:
    def __init__(self, x, y, th, rd):
        self.x, self.y, self.th, self.rd = x, y, th, rd
        self.vx, self.vy, self.vz = 0, 0, 0


# 全局控制变量
enabled = False
taxi_mode = False
stop_thread = False  # 控制子线程退出

# 全局变量初始化
Axis = AxisPos(0, 0, AXIS_MAX, 0)

# 输入状态跟踪
delta_x = 0
delta_y = 0


class MainWindow(QtWidgets.QMainWindow):
    dynamic_widgets = {}
    showCursor = QtCore.Signal(bool)
    showMessage = QtCore.Signal(str, str, int)
    lua = LuaRuntime(encoding='utf-8', unpack_returned_tuples=True)

    def __init__(self):
        super().__init__()
        init_logger(
            self.tr('MouseFlightControl'), APP_VERSION, self.show_startup_message
        )
        (
            self.screen_width,
            self.screen_height,
            self.center_x,
            self.center_y,
            self.scale,
        ) = self.get_screen_geometry(self.screen())
        self.w_size = 350
        self.min_w_size = self.px(300)
        self.max_w_size = self.px(500)
        self.input_width = 100
        self.apply_stylesheet()
        self.ui = Ui_MainWindow()
        self.message_box = MessageBox(self)

        # 程序状态
        self.main_thread = None
        self.debug = False
        self.running = False
        self.process = psutil.Process(os.getpid())
        self.original_mouse_speed = get_mouse_speed()
        self.target_fps = 250
        self.frame_interval = 1.0 / self.target_fps
        self.pause = 0.004

        # 其他状态
        self.attempts = 3
        self.indicator_x = 30
        self.indicator_y = -30
        self.indicator_bg_color = (255, 90, 0, 50)
        self.indicator_line_color = (255, 0, 0, 255)
        self.indicator_size = 200
        self.device = 'vjoy'
        self.device_id = 1
        self.axis_speed = 15
        self.damping_h = 1.0
        self.damping_v = 1.0

        # 配置默认值
        self.language = 'en_US'
        self.mouse_speed = 5
        self.key_toggle = '`'
        self.key_center = 'MMB'
        self.key_freecam = 'tab'
        self.key_view_center = 'capslock'
        self.camera_fov = 90
        self.key_taxi = 'alt + `'
        self.controller = 0
        self.show_cursor = False
        self.show_hint = True
        self.show_indicator = False
        self.button_mapping = True
        self.memorize_axis_pos = True
        self.freecam_auto_center = False
        self.__external__ = SimpleNamespace()

        # 加载所有配置
        self.load_config()

        self.setup_ui()

        # 加载配置的语言
        translator = QtCore.QTranslator()
        if translator.load(f'i18n/{self.language}.qm'):
            QtWidgets.QApplication.instance().installTranslator(translator)
            QtWidgets.QApplication.instance().translators.append(translator)

        # 脚本初始化和运行
        self.lua_globals = self.lua.globals()
        self.lua_lock = threading.Lock()
        self.lua_event = EventEmitter()
        self.lua_globals.SetAttribute = self._set_attr_value
        self.lua_globals.GetAttribute = self._get_attr_value
        self.lua_globals.GetLogger = get_logger
        self.lua_globals.AddEventHandler = lambda event, handler: self.lua_event.on(
            event, handler
        )
        self.lua_globals.RemoveEventHandler = lambda event: self.lua_event.off(event)
        self.lua.execute("""
            Axis = {x=0, y=0, th=0, rd=0, vx=0, vy=0, vz=0}
            Mouse = {speed=0, pos={0,0}, deltaX=0, deltaY=0}
            Input = {}
            Control = {active=false, steering=false}
            Camera = {active=false, fov=0}
            Screen = {}
        """)
        self.lua_globals.Axis.min = AXIS_MIN
        self.lua_globals.Axis.max = AXIS_MAX
        self.lua_globals.Axis.len = AXIS_LENGTH
        self.lua_globals.Axis.setValue = lambda axis, value: setattr(Axis, axis, value)
        self.lua_globals.Screen.renderMessage = (
            lambda text, color, duration: self.showMessage.emit(text, color, duration)
        )
        self.lua_globals.Mouse.speed = self.mouse_speed
        self.scripts = load_lua_scripts(self.lua, 'scripts', self.language)
        self.script_db = ScriptDatabase()
        for script in self.scripts:
            if hasattr(script, 'options'):
                config = load_config(
                    SCRIPT_INI_PATH, script.id, get_default(script.options)
                )
                self.script_db.add(script.id, config)

        self.lua_globals.GetConfig = lambda id: self.script_db.get(id)
        self.lua_funcs = []
        for script in self.scripts:
            script_config = self.script_db.get(script.id)
            if script_config:
                for k, v in validate_config(script_config, True).items():
                    self._set_attr_value(k, v)
            if script.data:
                try:
                    validate_config(script.data)
                    for k, v in script.data.items():
                        self._set_attr_value(k, v)
                except (TypeError, ValueError) as e:
                    logger.exception(str(e))
            if script.init:
                try:
                    script.init(self.script_db)
                except:
                    logger.exception(f"Script '{script.id}' has occured critical error")
            if script.update:
                self.lua_funcs.append(script.update)

        # 创建设备
        try:
            self.joystick = get_joystick_device(self.device, self.device_id)
            self.joystick.set_axis(HID_Z, AXIS_MAX)
        except RuntimeError as e:
            logger.error(str(e))
            self.message_box.error(self.tr('Error'), self.tr('DeviceNotFoundMessage'))

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
        self.ui.toggleEnabledKey.textChanged.connect(
            lambda text: self.update('key_toggle', text)
        )
        self.ui.centerControlKey.textChanged.connect(
            lambda text: self.update('key_center', text)
        )
        self.ui.enableFreecamKey.textChanged.connect(
            lambda text: self.update('key_freecam', text)
        )
        self.ui.viewCenterKey.textChanged.connect(
            lambda text: self.update('key_view_center', text)
        )
        self.ui.cameraFovSpinBox.valueChanged.connect(
            lambda value: self.update('camera_fov', value)
        )
        self.ui.taxiModeKey.textChanged.connect(
            lambda text: self.update('key_taxi', text)
        )
        self.ui.controllerComboBox.currentIndexChanged.connect(
            self.on_controller_changed
        )
        self.ui.showCursorOption.stateChanged.connect(
            lambda state: self.update('show_cursor', bool(state))
        )
        self.ui.showHintOption.stateChanged.connect(
            lambda state: self.update('show_hint', bool(state))
        )
        self.ui.showIndicatorOption.stateChanged.connect(
            lambda state: self.update('show_indicator', bool(state))
        )
        self.ui.buttonMappingOption.stateChanged.connect(
            lambda state: self.update('button_mapping', bool(state))
        )
        self.ui.memorizeAxisPosOption.stateChanged.connect(
            lambda state: self.update('memorize_axis_pos', bool(state))
        )
        self.ui.freecamAutoCenterOption.stateChanged.connect(
            lambda state: self.update('freecam_auto_center', bool(state))
        )

        self.hintLabel = HintLabel(self)
        self.showMessage.connect(self.hintLabel.show_message)
        self.cursorGraph = CursorGraph(self)
        self.showCursor.connect(self.cursorGraph.show_cursor)
        self.indicator = IndicatorWindow(
            self,
            self.indicator_x,
            self.indicator_y,
            self.indicator_bg_color,
            self.indicator_line_color,
            self.indicator_size,
            self.scale,
        )

        self.show()
        self.move(self.center_x - self.w_size / 2, self.center_y - self.height() / 2)
        logger.done()

    def get_stylesheet(self):
        assets_dir = 'assets/'
        if not os.path.exists(assets_dir):
            raise FileExistsError(
                "Cannot find 'assets' directory. Please verify the program's files are installed correctly."
            )

        self.input_width = self.px(self.input_width)

        return f"""
            QMainWindow {{
                background-color: #F0F0F0;
                font-size: 9pt;
            }}
            QWidget {{
                background-color: #F0F0F0;
            }}
            QLabel {{
                color: #000000;
            }}
            QPushButton {{
                background-color: #E1E1E1;
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #D0D0D0;
            }}
            QPushButton:pressed {{
                background-color: #C0C0C0;
                border: 1px solid #707070;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid #A0A0A0;
                height: 6px;
                background: #D0D0D0;
                margin: 2px 0;
            }}
            QSlider::handle:horizontal {{
                background: #E1E1E1;
                border: 1px solid #707070;
                width: 16px;
                margin: -4px 0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #F0F0F0;
            }}
            QSlider::add-page:horizontal {{
                background: #B0B0B0;
            }}
            QSlider::sub-page:horizontal {{
                background: #0078D7;
            }}
            QLineEdit {{
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: {self.input_width}px;
                max-width: {self.input_width}px;
            }}
            QSpinBox {{
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: {self.input_width}px;
                max-width: {self.input_width}px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: transparent;
                border: none;
                width: 16px;
            }}
            QSpinBox::up-arrow {{
                image: url({os.path.join(assets_dir, 'up_arrow.svg')});
                width: 16px;
                height: 16px;
            }}
            QSpinBox::down-arrow {{
                image: url({os.path.join(assets_dir, 'down_arrow.svg')});
                width: 16px;
                height: 16px;
            }}
            #controllerComboBox {{
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: 120px;
            }}
            #controllerComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #A0A0A0;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            #controllerComboBox::down-arrow {{
                image: url({os.path.join(assets_dir, 'down_arrow.svg')});
                width: 16px;
                height: 16px;
            }}
            #controllerComboBox QAbstractItemView {{
                border: 1px solid #A0A0A0;
                background: white;
                selection-background-color: #E1E1E1;
            }}
            #controlsTitleLabel, #optionsTitleLabel {{
                font-size: 14pt;
                font-weight: bold;
                color: #000000;
            }}
            #speedValueLabel {{
                color: #505050;
                font-size: 9pt;
                min-width: 30px;
            }}
        """

    def apply_stylesheet(self):
        """应用动态样式表"""
        stylesheet = self.get_stylesheet()
        self.setStyleSheet(stylesheet)

    def setup_ui(self):
        self.ui.setupUi(self)
        self.w_size = self.px(self.w_size)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setMinimumWidth(self.min_w_size)
        self.setMaximumWidth(self.max_w_size)

        font = QFont()
        font.setFamilies(['Segoe UI', 'Microsoft YaHei'])
        font.setPointSize(10)
        font.setWeight(QFont.Normal)
        QtWidgets.QApplication.instance().setFont(font)

    def setup_controllers(self):
        controllers.register(0, None, {'name': self.tr('None')})
        controllers.register(
            1,
            FixedWingController,
            {
                'name': self.tr('FixedWingMode'),
                'options': [
                    ('throttle_speed', OptionWidget.SpinBox, 100),
                    ('increase_throttle_speed', OptionWidget.LineEdit, 'shift'),
                    ('decrease_throttle_speed', OptionWidget.LineEdit, 'ctrl'),
                ],
                'i18n': {
                    'throttle_speed': {
                        'en_US': 'Throttle Speed',
                        'zh_CN': '节流阀速度',
                    },
                    'increase_throttle_speed': {
                        'en_US': 'Increase Speed (Hold)',
                        'zh_CN': '增加移动速度',
                    },
                    'decrease_throttle_speed': {
                        'en_US': 'Decrease Speed (Hold)',
                        'zh_CN': '减少移动速度',
                    },
                },
            },
        )
        controllers.register(
            2,
            HelicopterController,
            {
                'name': self.tr('HelicopterMode'),
                'options': [
                    ('collective_speed', OptionWidget.SpinBox, 125),
                    ('pedals_speed', OptionWidget.SpinBox, 125),
                ],
                'i18n': {
                    'collective_speed': {
                        'en_US': 'Collective Speed',
                        'zh_CN': '总距速度',
                    },
                    'pedals_speed': {
                        'en_US': 'Pedals Speed',
                        'zh_CN': '尾桨踏板速度',
                    },
                },
            },
        )
        index = self.controller
        self.ui.controllerComboBox.clear()
        for name in controllers.names():
            self.ui.controllerComboBox.addItem(name)
        self.ui.controllerComboBox.setCurrentIndex(index)

    def create_controller_widgets(self, id):
        """根据控制器元数据创建动态控件"""
        self.clear_controller_widgets()

        metadata = controllers.get_metadata(id)
        if not metadata or 'options' not in metadata:
            return

        # 为每个选项创建控件
        for option, widget, default in metadata['options']:
            # 创建水平布局
            h_layout = QtWidgets.QHBoxLayout()
            h_layout.setSpacing(10)  # 设置间距为10
            h_layout.setContentsMargins(0, 0, 0, 0)

            # 创建标签
            text = metadata.get('i18n', {}).get(option, {}).get(self.language, option)
            label = QtWidgets.QLabel(text)
            label.setObjectName(f'{option}Label')
            label.setMinimumWidth(self.px(150))
            h_layout.addWidget(label)

            # 添加水平弹簧
            spacer = QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
            )
            h_layout.addItem(spacer)

            if widget == OptionWidget.CheckBox:
                # 创建复选框
                checkbox = QtWidgets.QCheckBox()
                checkbox.setObjectName(f'{option}Option')
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
                    lambda state, opt=option: setattr(
                        self.__external__, opt, bool(state)
                    )
                )
                h_layout.addWidget(checkbox)

                self.dynamic_widgets[option] = {
                    'label': label,
                    'checkbox': checkbox,
                    'layout': h_layout,
                }

            elif widget == OptionWidget.LineEdit:
                # 创建文本输入
                line_edit = QtWidgets.QLineEdit()
                line_edit.setObjectName(f'{option}Option')
                # 应用动态宽度样式
                line_edit.setStyleSheet(f"""
                    QLineEdit {{
                        border: 1px solid #A0A0A0;
                        border-radius: 3px;
                        padding: 4px;
                        background: white;
                        min-width: {self.input_width}px;
                        max-width: {self.input_width}px;
                    }}
                """)

                if hasattr(self.__external__, option):
                    value = getattr(self.__external__, option)
                else:
                    value = default
                    setattr(self.__external__, option, value)

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
                    'layout': h_layout,
                }

            elif widget == OptionWidget.SpinBox:
                # 创建数值选择器
                spin_box = QtWidgets.QSpinBox()
                spin_box.setObjectName(f'{option}Option')
                # 应用动态宽度样式
                spin_box.setStyleSheet(f"""
                    QSpinBox {{
                        border: 1px solid #A0A0A0;
                        border-radius: 3px;
                        padding: 4px;
                        background: white;
                        min-width: {self.input_width}px;
                        max-width: {self.input_width}px;
                    }}
                    QSpinBox::up-button, QSpinBox::down-button {{
                        background: transparent;
                        border: none;
                        width: 16px;
                    }}
                """)
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
                    lambda value, opt=option: setattr(self.__external__, opt, value)
                )

                h_layout.addWidget(spin_box)

                self.dynamic_widgets[option] = {
                    'label': label,
                    'spin_box': spin_box,
                    'layout': h_layout,
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

    def get_script(self, id: str):
        arr = [scripts for scripts in self.scripts if scripts.id == id]
        i = len(arr)
        if i == 1:
            return arr[0]
        elif i >= 2:
            raise RuntimeError(f'Duplicate namespace: {id}')
        else:
            raise RuntimeError(f"'{id}' not found")

    def load_config(self, file: str = CONFIG_FILE):
        """从配置文件加载设置"""
        config = configparser.ConfigParser()

        if os.path.exists(file):
            try:
                config.read(file)
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
                logger.error(f'加载配置文件失败: {e}')
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
            logger.success('配置文件保存成功')
        except Exception as e:
            logger.error(f'保存配置文件失败: {e}')

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
        self.script_menu = self.menuBar().addMenu('')

        # 打开预设
        self.import_action = QtWidgets.QAction('', self)
        self.import_action.triggered.connect(self.open_preset)
        self.general_menu.addAction(self.import_action)

        # 添加语言选项
        self.language_group = QtWidgets.QActionGroup(self)
        self.language_group.setExclusive(True)
        # 英语
        self.english_action = QtWidgets.QAction('English', self)
        self.english_action.setCheckable(True)
        self.english_action.triggered.connect(lambda: self.change_language('en_US'))
        self.language_group.addAction(self.english_action)
        self.language_menu.addAction(self.english_action)
        self.english_action.setChecked(self.language == 'en_US')
        # 简体中文
        self.chinese_action = QtWidgets.QAction('简体中文', self)
        self.chinese_action.setCheckable(True)
        self.chinese_action.triggered.connect(lambda: self.change_language('zh_CN'))
        self.language_group.addAction(self.chinese_action)
        self.language_menu.addAction(self.chinese_action)
        self.chinese_action.setChecked(self.language == 'zh_CN')
        # 俄语
        self.russian_action = QtWidgets.QAction('Русский', self)
        self.russian_action.setCheckable(True)
        self.russian_action.triggered.connect(lambda: self.change_language('ru_RU'))
        self.language_group.addAction(self.russian_action)
        self.language_menu.addAction(self.russian_action)
        self.russian_action.setChecked(self.language == 'ru_RU')

        # 插件相关
        self.script_action = QtWidgets.QAction('', self)
        self.script_action.triggered.connect(lambda: open_directory('scripts'))
        self.script_menu.addAction(self.script_action)
        self.script_menu.addSeparator()
        self._script_actions: Dict[str, QtWidgets.QAction] = {}
        for script in self.scripts:
            self._script_actions[script.id] = QtWidgets.QAction(script.name, self)
            self._script_actions[script.id].triggered.connect(
                lambda *_, s=script: self.open_script_config(s)
            )
            self.script_menu.addAction(self._script_actions[script.id])

    def open_preset(self):
        if self.running:
            self.stop_main_thread()

        file_path = choose_single_file(self, self.tr('ImportPreset'), 'Inputs')
        if not file_path:
            return

        self.load_config(file_path)
        self.change_language(self.language)
        self.retranslate_ui()
        self.update_ui_state()

    def change_language(self, language_code):
        """更改应用程序语言"""
        for translator in QtWidgets.QApplication.instance().translators:
            QtWidgets.QApplication.instance().removeTranslator(translator)

        translator = QtCore.QTranslator()
        if translator.load(f'i18n/{language_code}.qm'):
            QtWidgets.QApplication.instance().installTranslator(translator)
            QtWidgets.QApplication.instance().translators.append(translator)

        self.language = language_code
        self.retranslate_ui()
        self.setup_controllers()
        self.create_controller_widgets(self.controller)

    def open_script_config(self, script: ScriptModule):
        window = ScriptWindow(script, self.script_db.get(script.id), self)
        window.show()

    def retranslate_ui(self):
        """重新翻译UI文本"""
        self.setWindowTitle(self.tr('Title'))
        self.general_menu.setTitle(self.tr('General'))
        self.import_action.setText(self.tr('ImportPreset'))
        self.language_menu.setTitle(self.tr('Language'))
        self.script_menu.setTitle(self.tr('Script'))
        self.script_action.setText(
            self.tr('Installed') + f' ({self.scripts.__len__()})'
        )

        for id, action in self._script_actions.items():
            script = self.get_script(id)
            script.set_language(self.language)
            action.setText(script.name)

        self.ui.startBtn.setText(
            self.tr('Start') if not self.running else self.tr('Stop')
        )
        self.ui.controlsTitleLabel.setText(self.tr('ControlsTitle'))
        self.ui.statusLabel.setText(
            self.tr('StatusStopped') if not enabled else self.tr('StatusWorking')
        )
        self.ui.speedLabel.setText(self.tr('Sensitive'))
        self.ui.speedValueLabel.setText(
            self.tr('CurrentValue') + f': {str(self.ui.mouseSpeedSlider.value())}'
        )
        self.ui.toggleEnabledLabel.setText(self.tr('ToggleEnabled'))
        self.ui.toggleEnabledKey.setText(self.key_toggle)
        self.ui.centerControlLabel.setText(self.tr('CenterControl'))
        self.ui.centerControlKey.setText(self.key_center)
        self.ui.enableFreecamLabel.setText(self.tr('EnableFreecam'))
        self.ui.enableFreecamKey.setText(self.key_freecam)
        self.ui.viewCenterLabel.setText(self.tr('ViewCenter'))
        self.ui.viewCenterKey.setText(self.key_view_center)
        self.ui.cameraFovLabel.setText(self.tr('CameraFov'))
        self.ui.cameraFovSpinBox.setValue(self.camera_fov)
        self.ui.taxiModeLabel.setText(self.tr('TaxiMode'))
        self.ui.taxiModeKey.setText(self.key_taxi)
        self.ui.controllerLabel.setText(self.tr('Controller'))
        self.ui.controllerComboBox.setCurrentIndex(self.controller)
        self.ui.controllerComboBox.setCurrentText(controllers.get_name(self.controller))
        self.ui.optionsTitleLabel.setText(self.tr('OptionsTitle'))
        self.ui.showCursorLabel.setText(self.tr('ShowCursor'))
        self.ui.showCursorOption.setChecked(self.show_cursor)
        self.ui.showHintLabel.setText(self.tr('HintOverlay'))
        self.ui.showHintOption.setChecked(self.show_hint)
        self.ui.showIndicatorLabel.setText(self.tr('ShowIndicator'))
        self.ui.showIndicatorOption.setChecked(self.show_indicator)
        self.ui.buttonMappingLabel.setText(self.tr('ButtonMapping'))
        self.ui.buttonMappingOption.setChecked(self.button_mapping)
        self.ui.memorizeAxisPosLabel.setText(self.tr('MemorizeAxisPos'))
        self.ui.memorizeAxisPosOption.setChecked(self.memorize_axis_pos)
        self.ui.freecamAutoCenterLabel.setText(self.tr('FreecamAutoCenter'))
        self.ui.freecamAutoCenterOption.setChecked(self.freecam_auto_center)

    def on_speed_changed(self, value):
        self.mouse_speed = value
        self.ui.speedValueLabel.setText(
            f'{self.tr("CurrentValue")}: {str(self.ui.mouseSpeedSlider.value())}'
        )
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
        self.ui.startBtn.setText(
            self.tr('Start') if not self.running else self.tr('Stop')
        )
        self.ui.statusLabel.setText(
            self.tr('StatusWorking') if disabled else self.tr('StatusStopped')
        )
        self.ui.mouseSpeedSlider.setDisabled(disabled)
        self.ui.toggleEnabledKey.setDisabled(disabled)
        self.ui.centerControlKey.setDisabled(disabled)
        self.ui.controllerComboBox.setDisabled(disabled)
        self.ui.enableFreecamKey.setDisabled(disabled)
        self.ui.viewCenterKey.setDisabled(disabled)
        self.ui.taxiModeKey.setDisabled(disabled)
        for option, controls in self.dynamic_widgets.items():
            if 'checkbox' in controls:
                controls['checkbox'].setDisabled(disabled)
            elif 'line_edit' in controls:
                controls['line_edit'].setDisabled(disabled)
            elif 'spin_box' in controls:
                controls['spin_box'].setDisabled(disabled)
        self.ui.showCursorOption.setDisabled(disabled)
        self.ui.showHintOption.setDisabled(disabled)
        self.ui.showIndicatorOption.setDisabled(disabled)
        self.ui.buttonMappingOption.setDisabled(disabled)
        self.ui.memorizeAxisPosOption.setDisabled(disabled)
        self.ui.freecamAutoCenterOption.setDisabled(disabled)
        self.ui.cameraFovSpinBox.setDisabled(disabled)

        self.ui.verticalLayout.invalidate()
        self.ui.verticalLayout.activate()
        QtWidgets.QApplication.processEvents()
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

        self.main_thread = threading.Thread(target=self.main, daemon=True)
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
        self.showCursor.emit(False)

    def closeEvent(self, event):
        """停止子线程"""
        global stop_thread
        stop_thread = True

        if self.main_thread:
            self.main_thread.join()

        self.w_size = int(self.size().width() / self.scale)
        self.save_config()
        save_config(SCRIPT_INI_PATH, self.script_db.to_dict())

        event.accept()

    def toggle_enabled(self, flag):
        if not self.running:
            return

        global enabled, taxi_mode
        enabled = flag

        if flag:
            set_mouse_speed(self.mouse_speed)
            if self.show_cursor:
                self.showCursor.emit(True)
            if self.show_hint:
                self.showMessage.emit(self.tr('Controlled'), 'green', 1000)
        else:
            set_mouse_speed(self.original_mouse_speed)
            self.showCursor.emit(False)
            if self.show_hint:
                self.showMessage.emit(self.tr('NoControl'), 'red', 1000)

        self.retranslate_ui()

    def main(self):
        global delta_x, delta_y, enabled, taxi_mode
        try:
            Class = controllers.get_class(self.controller)
            if Class:
                controller = Class(self.joystick)
            else:
                controller = None

            input = InputStateMonitor(self.pause, self.attempts)
            input.set_mouse_position(self.center_x, self.center_y)
            self.lua_globals.Input.pressed = input.is_pressed
            self.lua_globals.Input.pressing = input.is_pressing
            self.lua_globals.Input.released = input.is_released
            self.lua_globals.Input.alt = lambda: input.alt_ctrl_shift(alt=True)
            self.lua_globals.Input.ctrl = lambda: input.alt_ctrl_shift(ctrl=True)
            self.lua_globals.Input.shift = lambda: input.alt_ctrl_shift(shift=True)

            def map_to_percentage(value, reverse=False):
                clamped = max(AXIS_MIN, min(AXIS_MAX, value))
                return (
                    (clamped + AXIS_MAX) / AXIS_LENGTH
                    if not reverse
                    else 1 - (clamped + AXIS_MAX) / AXIS_LENGTH
                )

            prev_x, prev_y = self.center_x, self.center_y
            stick_pos = [self.center_x, self.center_y]
            cam_pos = [self.center_x, self.center_y]
            freecam_on = False
            use_cache = False

            if self.debug:
                loop_counter = 0  # 循环计数器
                frame_count = 0  # 帧计数器
                actual_fps = None
                debug_start_time = time.perf_counter()  # 调试计时起点

            last_frame_time = time.perf_counter()  # 上一帧开始时间

            while not stop_thread:  # 用stop_thread控制退出
                current_frame_time = time.perf_counter()
                target_end_time = last_frame_time + self.frame_interval
                sleep_time = target_end_time - current_frame_time
                delta_time = self.frame_interval
                if sleep_time > 0:
                    ctypes.windll.kernel32.Sleep(int(sleep_time * 1000 + 0.5))

                last_frame_time = target_end_time

                if self.debug:
                    frame_count += 1
                    if current_frame_time - debug_start_time >= 1.0:
                        actual_fps = frame_count / (
                            current_frame_time - debug_start_time
                        )
                        frame_count = 0
                        debug_start_time = current_frame_time

                    loop_counter += 1
                    if loop_counter % 500 == 0 and actual_fps:
                        cpu_usage = self.process.cpu_percent(interval=0.001)
                        memory_usage = self.process.memory_info().rss / 1024 / 1024
                        logger.debug(
                            f'FPS: {actual_fps:.1f} | CPU: {cpu_usage:.1f}% | Memory: {memory_usage:.2f}MB'
                        )

                input.update()

                if input.is_hotkey_pressed(self.key_toggle):
                    _flag = not enabled
                    self.toggle_enabled(_flag)
                    if self.memorize_axis_pos:
                        if not _flag:
                            stick_pos[0], stick_pos[1] = prev_x, prev_y
                        elif stick_pos[0] is not None and stick_pos[1] is not None:
                            prev_x, prev_y = stick_pos[0], stick_pos[1]
                            use_cache = True

                if input.is_hotkey_pressed(self.key_taxi):
                    if enabled:
                        taxi_mode = not taxi_mode
                        Axis.rd = 0
                        if taxi_mode:
                            if self.show_hint:
                                self.showMessage.emit(
                                    self.tr('TaxiModeOn'), 'green', 1000
                                )
                        else:
                            if self.show_hint:
                                self.showMessage.emit(
                                    self.tr('TaxiModeOff'), 'red', 1000
                                )

                if enabled and input.is_hotkey_pressed(self.key_center):
                    prev_x, prev_y = self.center_x, self.center_y
                    use_cache = True

                if enabled and input.is_hotkey_pressed(self.key_view_center):
                    Axis.vz = fov(self.camera_fov)
                    if not freecam_on:
                        Axis.vx, Axis.vy = 0, 0
                        cam_pos[0], cam_pos[1] = self.center_x, self.center_y

                if enabled and self.button_mapping and not freecam_on:
                    if input.is_pressing('LMB'):
                        self.joystick.set_button(1, True)
                    else:
                        self.joystick.set_button(1, False)
                    if input.is_pressing('RMB'):
                        self.joystick.set_button(2, True)
                    else:
                        self.joystick.set_button(2, False)
                    if input.is_pressing('MMB'):
                        self.joystick.set_button(3, True)
                    else:
                        self.joystick.set_button(3, False)
                    if input.is_pressing('XMB1'):
                        self.joystick.set_button(4, True)
                    else:
                        self.joystick.set_button(4, False)
                    if input.is_pressing('XMB2'):
                        self.joystick.set_button(5, True)
                    else:
                        self.joystick.set_button(5, False)

                if enabled:
                    if input.is_pressed(self.key_freecam):
                        freecam_on = True
                        stick_pos[0], stick_pos[1] = prev_x, prev_y
                        if self.freecam_auto_center:
                            Axis.vx, Axis.vy = 0, 0
                            prev_x, prev_y = self.center_x, self.center_y
                            use_cache = True
                        else:
                            prev_x, prev_y = cam_pos[0], cam_pos[1]
                            use_cache = True
                    if input.is_released(self.key_freecam):
                        freecam_on = False
                        cam_pos[0], cam_pos[1] = prev_x, prev_y
                        if self.freecam_auto_center:
                            Axis.vx, Axis.vy = 0, 0
                        prev_x, prev_y = stick_pos[0], stick_pos[1]
                        use_cache = True

                    if use_cache:
                        input.set_mouse_position(prev_x, prev_y)
                        use_cache = False

                    curr_x, curr_y = input.get_mouse_position()
                    delta_x = curr_x - prev_x
                    delta_y = curr_y - prev_y

                    if input.is_pressing(self.key_freecam) and freecam_on:
                        Axis.vx += delta_x * self.axis_speed * self.damping_h
                        Axis.vy += delta_y * self.axis_speed * self.damping_v

                        x_percent = Axis.vx / AXIS_MAX
                        y_percent = Axis.vy / AXIS_MAX
                        screen_x = self.center_x + x_percent * (self.screen_width / 2)
                        screen_y = self.center_y + y_percent * (self.screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        Axis.vx = check_overflow(Axis.vx, AXIS_MIN, AXIS_MAX)
                        Axis.vy = check_overflow(Axis.vy, AXIS_MIN, AXIS_MAX)

                        Axis.vz += wheel_step(
                            fov(10, abs=False), -input.get_wheel_delta()
                        )
                        Axis.vz = check_overflow(Axis.vz, AXIS_MIN, AXIS_MAX)
                    else:
                        Axis.x += delta_x * self.axis_speed * self.damping_h
                        Axis.y += delta_y * self.axis_speed * self.damping_v

                        x_percent = Axis.x / AXIS_MAX
                        y_percent = Axis.y / AXIS_MAX
                        screen_x = self.center_x + x_percent * (self.screen_width / 2)
                        screen_y = self.center_y + y_percent * (self.screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        Axis.x = check_overflow(Axis.x, AXIS_MIN, AXIS_MAX)
                        Axis.y = check_overflow(Axis.y, AXIS_MIN, AXIS_MAX)

                        if taxi_mode:
                            Axis.rd = Axis.x

                if enabled:
                    self.joystick.set_axis(HID_X, int(Axis.x))
                    self.joystick.set_axis(HID_Y, int(Axis.y))
                    self.joystick.set_axis(HID_Z, int(Axis.th))
                    self.joystick.set_axis(HID_RZ, int(Axis.rd))
                    self.joystick.set_axis(HID_RX, int(Axis.vx))
                    self.joystick.set_axis(HID_RY, int(Axis.vy))
                    self.joystick.set_axis(HID_SLIDER, int(Axis.vz))

                if controller is not None and isinstance(controller, BaseController):
                    controller.update(
                        Axis,
                        self.__external__,
                        input,
                        SimpleNamespace(enabled=enabled, dt=delta_time),
                        self,
                    )

                with self.lua_lock:
                    self.lua_globals.Axis['x'] = Axis.x
                    self.lua_globals.Axis['y'] = Axis.y
                    self.lua_globals.Axis['th'] = Axis.th
                    self.lua_globals.Axis['rd'] = Axis.rd
                    self.lua_globals.Axis['vx'] = Axis.vx
                    self.lua_globals.Axis['vy'] = Axis.vy
                    self.lua_globals.Axis['vz'] = Axis.vz
                    self.lua_globals.Mouse.pos[1] = prev_x
                    self.lua_globals.Mouse.pos[2] = prev_y
                    self.lua_globals.Mouse.deltaX = curr_x - prev_x
                    self.lua_globals.Mouse.deltaY = curr_y - prev_y
                    self.lua_globals.Control['active'] = enabled and not freecam_on
                    self.lua_globals.Control['steering'] = (
                        enabled and not freecam_on and taxi_mode
                    )
                    self.lua_globals.Camera['active'] = enabled and freecam_on
                    self.lua_globals.Camera['fov'] = axis2fov(Axis.vz)

                for i, func in enumerate(self.lua_funcs):
                    try:
                        func(delta_time)
                    except Exception as e:
                        print(f'Lua func {i} error: \n{e}')

                if self.show_indicator:
                    x_val = map_to_percentage(Axis.x)
                    y_val = map_to_percentage(Axis.y)
                    throttle_val = map_to_percentage(Axis.th, True)
                    rudder_val = map_to_percentage(Axis.rd)
                    self.update_indicator(x_val, y_val, throttle_val, rudder_val)

                input.reset_wheel_delta()

        except KeyboardInterrupt as e:
            logger.warning(f'Keyboard interrupt: {e}')
        except Exception as e:
            logger.error(f'Main thread exception: {e}')
            import traceback

            traceback.print_exc()
        finally:
            set_mouse_speed(self.original_mouse_speed)
            self.joystick.reset()
            input.cleanup()
            del input

    def get_screen_geometry(self, screen: QScreen):
        if not screen:
            screen = QtWidgets.QApplication.primaryScreen()

        logical_rect = screen.geometry()
        width = logical_rect.width()
        height = logical_rect.height()
        center_x = width / 2
        center_y = height / 2

        scale = 1.0
        if os.name == 'nt':
            try:
                user32 = ctypes.windll.user32
                hwnd = self.winId()
                dpi_x = user32.GetDpiForWindow(hwnd)
                scale = dpi_x / 96.0
            except:
                scale = screen.devicePixelRatio()

        return width, height, center_x, center_y, scale

    def px(self, pt: int):
        return int(pt * self.scale)

    def axis_to_screen(self, axis_x, axis_y):
        x_percent = axis_x / AXIS_MAX
        y_percent = axis_y / AXIS_MAX

        screen_x = self.center_x + x_percent * (self.screen_width / 2)
        screen_y = self.center_y + y_percent * (self.screen_height / 2)

        return screen_x, screen_y

    def update_indicator(self, x, y, throttle, rudder):
        self.indicator.set_xy_values(x, y)
        self.indicator.set_throttle_value(throttle)
        self.indicator.set_rudder_value(rudder)

    def show_startup_message(self, logger):
        dpi_aware = get_process_dpi_awareness()
        logger.opt(colors=True).info(
            f'<green>屏幕信息：</green> 分辨率: {self.screen_width}x{self.screen_height} | 缩放: {self.scale} | {dpi_aware[1]}'
        )
        if self.debug:
            logger.info('')
            logger.opt(colors=True).info('<yellow>调试模式已启用</yellow>')


if __name__ == '__main__':
    set_process_dpi_awareness(2)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = App(sys.argv)

    if not os.path.exists('i18n'):
        error_msg = QtWidgets.QMessageBox()
        error_msg.setIcon(QtWidgets.QMessageBox.Critical)
        error_msg.setText('Missing translation files')
        error_msg.setInformativeText(
            "Cannot find 'i18n' directory. Please verify the program's files are installed correctly."
        )
        error_msg.setWindowTitle('PATH NOT FOUND')
        error_msg.exec_()
        sys.exit(1)

    translator = QtCore.QTranslator()
    if translator.load('i18n/en_US.qm'):
        app.installTranslator(translator)
        app.translators.append(translator)

    window = MainWindow()

    sys.exit(app.exec_())
