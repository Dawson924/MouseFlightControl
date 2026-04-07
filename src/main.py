import os
import sys
import threading
import time
from types import SimpleNamespace
from typing import Dict

import psutil
from lupa import LuaRuntime
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QCoreApplication, QMetaObject, QSize, Qt, Slot
from PySide2.QtGui import QFont, QIcon

import i18n
from app import App
from common.axis import (
    AXIS_LENGTH,
    AXIS_MAX,
    AXIS_MIN,
    AXIS_RX,
    AXIS_RY,
    AXIS_RZ,
    AXIS_SL,
    AXIS_X,
    AXIS_Y,
    AXIS_Z,
    AxisPos,
)
from common.config import LANGUAGE_CONFIG
from common.constants import APP_VERSION, SCRIPT_INI_PATH
from controller.base import BaseController
from flightsim.module import controller_manager, load_modules
from input import InputStateMonitor
from lib.axis import axis2fov, fov, set_axis
from lib.config import load_all_data, save_all_data
from lib.event import EventEmitter
from lib.fs import open_directory
from lib.joystick import get_joystick_device
from lib.logger import get_logger, init_logger, logger
from lib.screen import ScreenGeometry
from lib.script import get_default, load_data, save_data, validate_config
from lib.win32 import (
    MessageBox,
    get_mouse_speed,
    set_mouse_speed,
)
from script_engine.database import ScriptDatabase
from script_engine.runtime import load_lua_scripts
from type.script import ScriptModule
from ui.MainWindow import Ui_MainWindow
from ui.page import ConnectPage, ControlsPage, OptionsPage, TunePage
from ui.screen.CursorGraph import CursorGraph
from ui.screen.HintLabel import HintLabel
from ui.screen.IndicatorWindow import IndicatorWindow
from ui.window.script import ScriptWindow
from utils import check_overflow, wheel_step

input = None

enabled = False
stop_thread = False

delta_x = 0
delta_y = 0


class MainWindow(QtWidgets.QMainWindow):
    showCursor = QtCore.Signal(bool)
    showMessage = QtCore.Signal(str, str, int)
    lua = LuaRuntime(encoding='utf-8', unpack_returned_tuples=True)

    def __init__(self):
        super().__init__()
        self.win = ScreenGeometry(self.winId(), self.screen())

        self.screen_width = self.win.screen_width
        self.screen_height = self.win.screen_height
        self.center_x = self.win.center_x
        self.center_y = self.win.center_y
        self.scale = self.win.scale
        self.px = self.win.px

        self.min_w_size = self.win.px(350)
        self.max_w_size = self.win.px(550)
        self.input_width = 100

        self.apply_stylesheet()

        self.ui = Ui_MainWindow()
        self.message_box = MessageBox(self)

        self.main_thread = None
        self.debug = False
        self.running = False
        self.process = psutil.Process(os.getpid())
        self.original_mouse_speed = get_mouse_speed()
        self.target_fps = 250
        self.frame_interval = 1.0 / self.target_fps

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

        self.config, self.flightdata = load_all_data()

        i18n.set('locale', self.config.get('language'))

        self.init_joystick()
        self.init_scripts()

        self.init_ui()
        self.create_menu()

        self.retranslate_ui()
        self.update_ui()

        self.ui.startButton.clicked.connect(self.on_startButton_clicked)

        self.hintLabel = HintLabel(self)
        self.showMessage.connect(self.hintLabel.show_message)
        self.cursorGraph = CursorGraph(self)
        self.showCursor.connect(self.cursorGraph.show_cursor)
        self.indicator = IndicatorWindow(
            None,
            self.indicator_x,
            self.indicator_y,
            self.indicator_bg_color,
            self.indicator_line_color,
            self.indicator_size,
            self.scale,
        )

        self.show()
        self.resize(QSize(self.config.get('width'), self.config.get('height')))
        self.move(self.center_x - self.config.get('width') / 2, self.center_y - self.height() / 2)

        logger.done(self.show_message)

    def get_stylesheet(self):
        assets_dir = 'assets/'
        if not os.path.exists(assets_dir):
            raise FileExistsError(
                "Cannot find 'assets' directory. Please verify the program's files are installed correctly."
            )

        style = f"""
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
            QPushButton#startButton {{
                background-color: #E1E1E1;
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }}
            QPushButton#startButton:hover {{
                background-color: #D0D0D0;
            }}
            QPushButton#startButton:pressed {{
                background-color: #C0C0C0;
                border: 1px solid #707070;
            }}
            QPushButton {{
                font-family: "Segoe UI", "Microsoft YaHei", Arial;
                font-size: 9pt;
                padding: 1px 5px;
                min-height: 25px;
                min-width: 35px;
                background-color: #F0F0F0;
                border: 1px solid #B0B0B0;
                border-radius: 3px;
                color: #000000;
            }}
            QPushButton:hover {{
                background-color: #E5E5E5;
                border-color: #909090;
            }}
            QPushButton:disabled {{
                background-color: #F8F8F8;
                border-color: #D0D0D0;
                color: #A0A0A0;
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
            QComboBox {{
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: 120px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #A0A0A0;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QComboBox::down-arrow {{
                image: url({os.path.join(assets_dir, 'down_arrow.svg')});
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
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
        return style

    def apply_stylesheet(self):
        stylesheet = self.get_stylesheet()
        self.setStyleSheet(stylesheet)

    def init_ui(self):
        self.ui.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setMinimumWidth(self.min_w_size)
        self.setMaximumWidth(self.max_w_size)

        if self.config.get('width') == 0:
            self.config.set('width', self.win.px(350))
        if self.config.get('height') == 0:
            self.config.set('height', self.win.px(550))

        font = QFont()
        font.setFamilies(['Segoe UI', 'Microsoft YaHei'])
        font.setPointSize(10)
        font.setWeight(QFont.Normal)
        QtWidgets.QApplication.instance().setFont(font)
        QMetaObject.connectSlotsByName(self)
        self.init_pages()

    def init_pages(self):
        self.modules = load_modules()
        self.connect_page = ConnectPage(self.win, self.config, self.flightdata, self.modules)
        self.connect_page.state_changed.connect(self.update_ui)
        self.ui.connectPageLayout.addWidget(self.connect_page)

        self.controls_page = ControlsPage(self.win, self.config, self.flightdata)
        self.ui.controlsPageLayout.addWidget(self.controls_page)

        self.options_page = OptionsPage(self.win, self.config, self.flightdata)
        self.ui.optionsPageLayout.addWidget(self.options_page)

        self.tune_page = TunePage(self.win, self.config, self.flightdata)
        self.ui.axisTunePageLayout.addWidget(self.tune_page)

    def init_joystick(self):
        try:
            self.axis = AxisPos(0, 0, AXIS_MIN, 0, 0, 0, fov(self.flightdata.get('camera_fov')))
            self.joystick = get_joystick_device(self.device, self.device_id)
        except RuntimeError as e:
            logger.error(str(e))
            self.message_box.error(i18n.t('Error'), i18n.t('DeviceNotFoundMessage'))

    def init_scripts(self):
        self.lua_globals = self.lua.globals()
        self.lua_lock = threading.Lock()
        self.lua_event = EventEmitter()
        self.lua_globals.SetAttribute = self._set_attr_value
        self.lua_globals.GetAttribute = self._get_attr_value
        self.lua_globals.GetLogger = get_logger
        self.lua_globals.GetMouseSpeed = get_mouse_speed
        self.lua_globals.SetMouseSpeed = set_mouse_speed
        self.lua_globals.AddEventHandler = lambda event, handler: self.lua_event.on(event, handler)
        self.lua_globals.RemoveEventHandler = lambda event: self.lua_event.off(event)
        self.lua.execute("""
            Axis = {x=0, y=0, th=0, rd=0, vx=0, vy=0, vz=0}
            Mouse = {speed=0, pos={0,0}, deltaX=0, deltaY=0}
            Input = {}
            Control = {active=false, steering=false}
            Camera = {active=false, fov=0}
            Screen = {}
        """)
        self.lua_globals.Axis = self.axis
        self.lua_globals.AXIS_MIN = AXIS_MIN
        self.lua_globals.AXIS_MAX = AXIS_MAX
        self.lua_globals.AXIS_LEN = AXIS_LENGTH
        self.lua_globals.SetAxis = lambda axis, value: set_axis(self.axis, axis, value)
        self.lua_globals.Screen.renderMessage = lambda text, color, duration: self.showMessage.emit(
            text, color, duration
        )
        self.lua_globals.Mouse.speed = self.config.get('mouse_speed')
        self.scripts = load_lua_scripts(self.lua, 'scripts', self.config.get('language'))
        self.script_db = ScriptDatabase()
        for script in self.scripts:
            if hasattr(script, 'options'):
                config = load_data(SCRIPT_INI_PATH, script.id, get_default(script.options))
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

    def get_script(self, id: str):
        arr = [scripts for scripts in self.scripts if scripts.id == id]
        i = len(arr)
        if i == 1:
            return arr[0]
        elif i >= 2:
            raise RuntimeError(f'Duplicate namespace: {id}')
        else:
            raise RuntimeError(f"'{id}' not found")

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

        self.import_action = QtWidgets.QAction('', self)
        self.general_menu.addAction(self.import_action)

        self.language_group = QtWidgets.QActionGroup(self)
        self.language_group.setExclusive(True)
        self.language_actions = {}
        for lang in LANGUAGE_CONFIG:
            action = QtWidgets.QAction(lang['display_name'], self)
            action.setCheckable(True)
            action.triggered.connect(lambda *_, code=lang['code']: self.change_language(code))
            self.language_group.addAction(action)
            self.language_menu.addAction(action)
            action.setChecked(self.config.get('language') == lang['code'])
            self.language_actions[lang['code']] = action

        self.script_action = QtWidgets.QAction('', self)
        self.script_action.triggered.connect(lambda: open_directory('scripts'))
        self.script_menu.addAction(self.script_action)
        self.script_menu.addSeparator()
        self._script_actions: Dict[str, QtWidgets.QAction] = {}
        for script in self.scripts:
            self._script_actions[script.id] = QtWidgets.QAction(script.name, self)
            self._script_actions[script.id].triggered.connect(lambda *_, s=script: self.on_scriptButton_clicked(s))
            self.script_menu.addAction(self._script_actions[script.id])

    def change_language(self, language_code):
        self.config.set('language', language_code)
        i18n.set('locale', language_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(i18n.t('Title', version=f'{APP_VERSION}'))
        self.general_menu.setTitle(i18n.t('General'))
        self.import_action.setText(i18n.t('ImportPreset'))
        self.language_menu.setTitle(i18n.t('Language'))
        self.script_menu.setTitle(i18n.t('Script'))
        self.script_action.setText(i18n.t('Installed') + f' ({self.scripts.__len__()})')

        self.connect_page.retranslate_ui()
        self.controls_page.retranslate_ui()
        self.options_page.retranslate_ui()
        self.tune_page.retranslate_ui()

        for id, action in self._script_actions.items():
            script = self.get_script(id)
            script.set_language(self.config.get('language'))
            action.setText(script.name)

        self.ui.startButton.setText(i18n.t('Start') if not self.running else i18n.t('Stop'))
        self.ui.tabWidget.setTabText(0, i18n.t('ConnectPage'))
        self.ui.tabWidget.setTabText(1, i18n.t('ControlsPage'))
        self.ui.tabWidget.setTabText(2, i18n.t('OptionsPage'))
        self.ui.tabWidget.setTabText(3, i18n.t('TunePage'))
        self.ui.statusLabel.setText(i18n.t('StatusStopped') if not enabled else i18n.t('StatusWorking'))

    @Slot()
    def on_startButton_clicked(self):
        if not self.running:
            self.running = True
            self.start_main_thread()
        else:
            self.running = False
            self.toggle_enabled(False)
            self.stop_main_thread()

        self.update_ui()

    def on_scriptButton_clicked(self, script: ScriptModule):
        window = ScriptWindow(script, self.script_db.get(script.id), self)
        window.show()

    def update_ui(self):
        disabled = self.running
        self.ui.startButton.setText(i18n.t('Start') if not self.running else i18n.t('Stop'))
        self.ui.statusLabel.setText(i18n.t('StatusWorking') if disabled else i18n.t('StatusStopped'))

    def start_main_thread(self):
        global stop_thread, enabled
        stop_thread = False
        enabled = False

        if self.main_thread and self.main_thread.is_alive():
            return

        if self.config.get('show_indicator'):
            self.indicator.show_overlay(True)

        self.main_thread = threading.Thread(target=self.main, daemon=True)
        self.main_thread.start()

    def stop_main_thread(self):
        global stop_thread, enabled
        stop_thread = True
        enabled = False

        if self.main_thread and self.main_thread.is_alive():
            self.main_thread.join()

        self.indicator.show_overlay(False)

        self.main_thread = None
        self.showCursor.emit(False)

    def closeEvent(self, event):
        global stop_thread, input
        stop_thread = True

        if self.main_thread:
            self.main_thread.join()

        if input:
            input.stop_wheel_listener()

        size = self.size()
        self.config.set('width', size.width())
        self.config.set('height', size.height())
        save_all_data((self.config, self.flightdata))
        save_data(SCRIPT_INI_PATH, self.script_db.to_dict())
        event.accept()

    def toggle_enabled(self, flag):
        if not self.running:
            return

        global enabled
        enabled = flag

        if flag:
            set_mouse_speed(self.config.get('mouse_speed'))
            if self.config.get('show_cursor'):
                self.showCursor.emit(True)
            if self.config.get('show_hint'):
                self.showMessage.emit(i18n.t('Controlled'), 'green', 1000)
        else:
            set_mouse_speed(self.original_mouse_speed)
            self.showCursor.emit(False)
            if self.config.get('show_hint'):
                self.showMessage.emit(i18n.t('NoControl'), 'red', 1000)

    def main(self):
        global delta_x, delta_y, enabled, input
        try:
            if not input:
                input = InputStateMonitor()

            self.joystick.update_filters(self.flightdata.get_filters())

            config = self.config
            flight = self.flightdata

            Class = controller_manager.get_class(flight['Input']['flight_mode'])
            if Class:
                controller = Class(self.joystick, self.flightdata)
            else:
                controller = None

            self.lua_globals.Control.mode = flight['Input']['flight_mode']

            input.set_mouse_position(self.center_x, self.center_y)
            self.lua_globals.Input.pressed = input.is_pressed
            self.lua_globals.Input.pressing = input.is_pressing
            self.lua_globals.Input.released = input.is_released
            self.lua_globals.Input.hotkey = input.is_hotkey_pressed
            self.lua_globals.Input.alt = lambda: input.alt_ctrl_shift(alt=True)
            self.lua_globals.Input.ctrl = lambda: input.alt_ctrl_shift(ctrl=True)
            self.lua_globals.Input.shift = lambda: input.alt_ctrl_shift(shift=True)
            self.lua_globals.Input.modkey = lambda: input.alt_ctrl_shift

            def map_to_percentage(value, reverse=False):
                clamped = max(AXIS_MIN, min(AXIS_MAX, value))
                return (clamped + AXIS_MAX) / AXIS_LENGTH if not reverse else 1 - (clamped + AXIS_MAX) / AXIS_LENGTH

            curr_x, curr_y = self.center_x, self.center_y
            prev_x, prev_y = self.center_x, self.center_y
            stick_pos = [self.center_x, self.center_y]
            cam_pos = [self.center_x, self.center_y]
            freecam_on = False
            ground_taxi = False
            jump = False

            if self.debug:
                loop_counter = 0
                frame_count = 0
                actual_fps = None
                debug_start_time = time.perf_counter()

            last_frame_time = time.perf_counter()

            while not stop_thread:
                current_frame_time = time.perf_counter()
                target_end_time = last_frame_time + self.frame_interval
                sleep_time = target_end_time - current_frame_time
                delta_time = self.frame_interval
                if sleep_time > 0:
                    time.sleep(sleep_time)

                last_frame_time = target_end_time

                if self.debug:
                    frame_count += 1
                    if current_frame_time - debug_start_time >= 1.0:
                        actual_fps = frame_count / (current_frame_time - debug_start_time)
                        frame_count = 0
                        debug_start_time = current_frame_time

                    loop_counter += 1
                    if loop_counter % 500 == 0 and actual_fps:
                        cpu_usage = self.process.cpu_percent()
                        memory_usage = self.process.memory_info().rss / 1024 / 1024
                        logger.debug(f'FPS: {actual_fps:.1f} | CPU: {cpu_usage:.1f}% | Memory: {memory_usage:.2f}MB')

                input.update()

                if input.is_hotkey_pressed(config['key_toggle']):
                    _flag = not enabled
                    self.toggle_enabled(_flag)
                    if config['memorize_axis_pos']:
                        if not _flag:
                            stick_pos[0], stick_pos[1] = prev_x, prev_y
                        elif stick_pos[0] is not None and stick_pos[1] is not None:
                            prev_x, prev_y = stick_pos[0], stick_pos[1]
                            jump = True

                if enabled and input.is_hotkey_pressed(config['key_taxi']):
                    ground_taxi = not ground_taxi
                    self.axis.rd = 0
                    if ground_taxi:
                        if config['show_hint']:
                            self.showMessage.emit(i18n.t('TaxiModeOn'), 'green', 1000)
                    else:
                        if config['show_hint']:
                            self.showMessage.emit(i18n.t('TaxiModeOff'), 'red', 1000)

                if enabled and input.is_hotkey_pressed(config['key_center']):
                    prev_x, prev_y = self.center_x, self.center_y
                    jump = True

                if enabled and input.is_hotkey_pressed(config['key_view_center']):
                    self.axis.vz = fov(flight['Input']['camera_fov'])
                    if not freecam_on:
                        self.axis.vx, self.axis.vy = 0, 0
                        cam_pos[0], cam_pos[1] = self.center_x, self.center_y

                if enabled and config['button_mapping'] and not freecam_on:
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
                    if input.is_pressed(config['key_freecam']):
                        freecam_on = True
                        stick_pos[0], stick_pos[1] = prev_x, prev_y
                        if config['freecam_auto_center']:
                            self.axis.vx, self.axis.vy = 0, 0
                            prev_x, prev_y = self.center_x, self.center_y
                            jump = True
                        else:
                            prev_x, prev_y = cam_pos[0], cam_pos[1]
                            jump = True
                    if input.is_released(config['key_freecam']):
                        freecam_on = False
                        cam_pos[0], cam_pos[1] = prev_x, prev_y
                        if config['freecam_auto_center']:
                            self.axis.vx, self.axis.vy = 0, 0
                        prev_x, prev_y = stick_pos[0], stick_pos[1]
                        jump = True

                    if jump:
                        input.set_mouse_position(prev_x, prev_y)
                        jump = False

                    curr_x, curr_y = input.get_mouse_position()
                    delta_x = curr_x - prev_x
                    delta_y = curr_y - prev_y

                    if freecam_on:
                        self.axis.vx += delta_x * self.axis_speed * self.damping_h
                        self.axis.vy += delta_y * self.axis_speed * self.damping_v

                        x_percent = self.axis.vx / AXIS_MAX
                        y_percent = self.axis.vy / AXIS_MAX
                        screen_x = self.center_x + x_percent * (self.screen_width / 2)
                        screen_y = self.center_y + y_percent * (self.screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        self.axis.vz += wheel_step(fov(10, abs=False), input.get_wheel_delta())
                    else:
                        self.axis.x += delta_x * self.axis_speed * self.damping_h
                        self.axis.y += delta_y * self.axis_speed * self.damping_v

                        x_percent = self.axis.x / AXIS_MAX
                        y_percent = self.axis.y / AXIS_MAX
                        screen_x = self.center_x + x_percent * (self.screen_width / 2)
                        screen_y = self.center_y + y_percent * (self.screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        if ground_taxi:
                            self.axis.rd = self.axis.x

                if controller and isinstance(controller, BaseController):
                    controller.update(
                        self.axis,
                        input,
                        SimpleNamespace(enabled=enabled, dt=delta_time),
                        self,
                    )

                with self.lua_lock:
                    self.lua_globals.Mouse.pos[1] = prev_x
                    self.lua_globals.Mouse.pos[2] = prev_y
                    self.lua_globals.Mouse.deltaX = curr_x - prev_x
                    self.lua_globals.Mouse.deltaY = curr_y - prev_y
                    self.lua_globals.Control['active'] = enabled and not freecam_on
                    self.lua_globals.Control['steering'] = enabled and not freecam_on and ground_taxi
                    self.lua_globals.Camera['active'] = enabled and freecam_on
                    self.lua_globals.Camera['fov'] = axis2fov(self.axis.vz)

                for i, func in enumerate(self.lua_funcs):
                    try:
                        func(delta_time)
                    except Exception as e:
                        logger.error(f'Lua script error: \n{e}')
                        self.lua_funcs.pop(i)

                if enabled:
                    self.axis.x = check_overflow(self.axis.x, AXIS_MIN, AXIS_MAX)
                    self.axis.y = check_overflow(self.axis.y, AXIS_MIN, AXIS_MAX)
                    self.axis.th = check_overflow(self.axis.th, AXIS_MIN, AXIS_MAX)
                    self.axis.rd = check_overflow(self.axis.rd, AXIS_MIN, AXIS_MAX)
                    self.axis.vx = check_overflow(self.axis.vx, AXIS_MIN, AXIS_MAX)
                    self.axis.vy = check_overflow(self.axis.vy, AXIS_MIN, AXIS_MAX)
                    self.axis.vz = check_overflow(self.axis.vz, AXIS_MIN, AXIS_MAX)
                    self.joystick.set_axis(AXIS_X, int(self.axis.x))
                    self.joystick.set_axis(AXIS_Y, int(self.axis.y))
                    self.joystick.set_axis(AXIS_Z, int(self.axis.th))
                    self.joystick.set_axis(AXIS_RZ, int(self.axis.rd))
                    self.joystick.set_axis(AXIS_RX, int(self.axis.vx))
                    self.joystick.set_axis(AXIS_RY, int(self.axis.vy))
                    self.joystick.set_axis(AXIS_SL, int(self.axis.vz))

                if config['show_indicator']:
                    x_val = map_to_percentage(self.axis.x)
                    y_val = map_to_percentage(self.axis.y)
                    throttle_val = map_to_percentage(self.axis.th)
                    rudder_val = map_to_percentage(self.axis.rd)
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

    def update_indicator(self, x, y, throttle, rudder):
        self.indicator.set_xy_values(x, y)
        self.indicator.set_throttle_value(throttle)
        self.indicator.set_rudder_value(rudder)

    def show_message(self, logger):
        logger.opt(colors=True).info(
            f'<green>{i18n.t("ScreenInfo")}: </green> {self.screen_width}x{self.screen_height} | DPI: {self.scale}'
        )
        if self.debug:
            logger.info('')
            logger.opt(colors=True).info(f'<yellow>{i18n.t("DebugEnabled")}</yellow>')


if __name__ == '__main__':
    try:
        init_logger()

        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

        app = App(sys.argv)

        try:
            app.setWindowIcon(QIcon('assets/icon.ico'))
            logger.info('Window icon set successfully')
        except Exception as e:
            logger.warning(f'Error setting window icon: {e}')

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

        i18n.load_path.append('i18n')
        i18n.set('available_locales', [lang['code'] for lang in LANGUAGE_CONFIG])
        i18n.set('skip_locale_root_data', True)
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('locale', 'en_US')
        i18n.set('fallback', 'en_US')
        logger.info('i18n initialized successfully')

        window = MainWindow()
        logger.info('Window created successfully')

        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f'Critical error during startup: {e}')

        import traceback

        traceback.print_exc()

        error_msg = QtWidgets.QMessageBox()
        error_msg.setIcon(QtWidgets.QMessageBox.Critical)
        error_msg.setText('Critical Error')
        error_msg.setInformativeText(f'An error occurred during startup: {e}')
        error_msg.setWindowTitle('ERROR')
        error_msg.exec_()

        sys.exit(1)
