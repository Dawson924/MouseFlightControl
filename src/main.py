import os
import sys
import threading
import time
from types import SimpleNamespace

import psutil
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QCoreApplication, QMetaObject, QSize, Qt, Slot
from PySide2.QtGui import QFont, QIcon

import i18n
from app import App
from common.axis import (
    AXIS_LENGTH,
    AXIS_MAX,
    AXIS_MIN,
    AxisPos,
)
from common.config import LANGUAGE_CONFIG
from common.constants import APP_VERSION, EXTENSIONS_PATH
from connect.controller import controllers
from connect.flight import FlightConnect
from connect.platform import load_modules
from input import InputDevices
from lib.axis import axis2fov, fov
from lib.config import load_all_data, save_all_data
from lib.data import registry
from lib.event import events
from lib.joystick import get_joystick_device
from lib.log import init_logger, logger
from lib.screen import ScreenGeometry
from lib.win32 import (
    MessageBox,
    get_mouse_speed,
    set_mouse_speed,
)
from plugin import extension_loader
from ui.MainWindow import Ui_MainWindow
from ui.page import ConnectPage, ControlsPage, OptionsPage, TunePage
from ui.screen.CursorGraph import CursorGraph
from ui.screen.HintLabel import HintLabel
from ui.screen.IndicatorWindow import IndicatorWindow
from ui.window.extension import ExtensionWindow
from utils import check_overflow, wheel_step

input = None

enabled = False
stop_thread = False

delta_x = 0
delta_y = 0


class MainWindow(QtWidgets.QMainWindow):
    showCursor = QtCore.Signal(bool)
    showMessage = QtCore.Signal(str, str, int)

    def __init__(self):
        super().__init__()
        self.win = ScreenGeometry(self.winId(), self.screen())

        self.screen_width = self.win.screen_width
        self.screen_height = self.win.screen_height
        self.center_x = self.win.center_x
        self.center_y = self.win.center_y
        self.scale = self.win.scale
        self.px = self.win.px

        self.min_w_size = self.px(350)
        self.max_w_size = self.px(550)
        self.input_width = 100

        self.apply_stylesheet()

        self.ui = Ui_MainWindow()

        self.main_thread: threading.Thread = None
        self.connector: FlightConnect = None
        self.debug: bool = False
        self.running: bool = False
        self.process: psutil.Process = psutil.Process(os.getpid())
        self.original_mouse_speed: int = get_mouse_speed()
        self.target_fps: int = 250
        self.frame_interval: float = 1.0 / self.target_fps

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
        registry.singleton('config', self.config)
        registry.singleton('flightdata', self.flightdata)

        i18n.set('locale', self.config.get('language'))

        self.init_joystick()

        self.indicator = IndicatorWindow(
            None,
            self.indicator_x,
            self.indicator_y,
            self.indicator_bg_color,
            self.indicator_line_color,
            self.indicator_size,
            self.scale,
        )

        self.init_extensions()

        self.modules = load_modules()
        registry.singleton('modules', self.modules)

        self.init_ui()
        self.create_menu()

        self.retranslate_ui()
        self.update_ui()

        events.on('model_changed', self.on_model_changed)

        self.ui.startButton.clicked.connect(self.on_startButton_clicked)

        self.hintLabel = HintLabel(self)
        self.showMessage.connect(self.hintLabel.show_message)
        self.cursorGraph = CursorGraph(self)
        self.showCursor.connect(self.cursorGraph.show_cursor)

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
        QMetaObject.connectSlotsByName(self)

        if self.config.get('width') == 0:
            self.config.set('width', self.win.px(350))
        if self.config.get('height') == 0:
            self.config.set('height', self.win.px(550))

        font = QFont()
        font.setFamilies(['Segoe UI', 'Microsoft YaHei'])
        font.setPointSize(10)
        font.setWeight(QFont.Normal)
        QtWidgets.QApplication.instance().setFont(font)

        self.message_box = MessageBox(self)
        registry.singleton('message_box', self.message_box)

        self.init_pages()

    def init_pages(self):
        self.connect_page = ConnectPage()
        self.ui.connectPageLayout.addWidget(self.connect_page)

        self.controls_page = ControlsPage()
        self.ui.controlsPageLayout.addWidget(self.controls_page)

        self.options_page = OptionsPage()
        self.ui.optionsPageLayout.addWidget(self.options_page)

        self.tune_page = TunePage()
        self.ui.axisTunePageLayout.addWidget(self.tune_page)

        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        self._pages = [
            self.connect_page,
            self.controls_page,
            self.options_page,
            self.tune_page,
        ]

    def init_joystick(self):
        try:
            self.axis = AxisPos(0, 0, AXIS_MIN, 0, 0, 0, fov(self.flightdata.get('camera_fov')))
            self.joystick = get_joystick_device(self.device, self.device_id)
            registry.singleton('joystick', self.joystick)
        except RuntimeError as e:
            logger.error(str(e))
            self.message_box.error(i18n.t('Error'), i18n.t('DeviceNotFoundMessage'))

    def init_extensions(self):
        registry.singleton('main_window', self)
        registry.singleton('axis', self.axis)
        registry.singleton('indicator', self.indicator)

        extension_loader.load(EXTENSIONS_PATH)
        extension_loader.start_all()

        logger.info(f'Extension system initialized. Loaded {len(extension_loader.extensions)} extensions')

    def create_menu(self):
        self.general_menu = self.menuBar().addMenu('')
        self.language_menu = self.menuBar().addMenu('')

        self.import_action = QtWidgets.QAction('', self)
        self.general_menu.addAction(self.import_action)

        self.extension_action = QtWidgets.QAction('', self)
        self.extension_action.triggered.connect(self.open_extension_window)
        self.general_menu.addAction(self.extension_action)

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

    def change_language(self, language_code):
        self.config.set('language', language_code)
        i18n.set('locale', language_code)
        self.retranslate_ui()

    def open_extension_window(self):
        self.extension_window = ExtensionWindow(self)
        self.extension_window.show()

    def retranslate_ui(self):
        self.setWindowTitle(i18n.t('Title', version=f'{APP_VERSION}'))
        self.general_menu.setTitle(i18n.t('General'))
        self.import_action.setText(i18n.t('ImportPreset'))
        self.extension_action.setText(i18n.t('Extensions'))
        self.language_menu.setTitle(i18n.t('Language'))

        self.connect_page.retranslate_ui()
        self.controls_page.retranslate_ui()
        self.options_page.retranslate_ui()
        self.tune_page.retranslate_ui()

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

    def on_tab_changed(self, index):
        if 0 <= index < len(self._pages):
            self._pages[index].update_ui()

    def on_model_changed(self, model):
        connector = self.connector
        if connector:
            if self.config.get('auto_connect') and not self.running:
                disabled = not model or model == 'Spectator'
                self.ui.startButton.setDisabled(disabled)
            else:
                self.ui.startButton.setDisabled(False)

        modules = registry.get('modules')
        extension_loader.on_model_changed(model, modules)

    def update_ui(self):
        self.ui.startButton.setText(i18n.t('Start') if not self.running else i18n.t('Stop'))
        self.ui.statusLabel.setText(i18n.t('StatusWorking') if self.running else i18n.t('StatusStopped'))

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

        extension_loader.stop_all()

        size = self.size()
        self.config.set('width', size.width())
        self.config.set('height', size.height())
        save_all_data((self.config, self.flightdata))
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
                input = InputDevices()

            self.joystick.update_filters(self.flightdata.get_filters())
            controllers.refresh_fields()

            config = self.config
            flight = self.flightdata

            input.set_mouse_position(self.center_x, self.center_y)

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
                    self.axis.Rudder = 0
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
                    self.axis.ZoomView = fov(flight['Input']['camera_fov'])
                    if not freecam_on:
                        self.axis.CamX, self.axis.CamY = 0, 0
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
                            self.axis.CamX, self.axis.CamY = 0, 0
                            prev_x, prev_y = self.center_x, self.center_y
                            jump = True
                        else:
                            prev_x, prev_y = cam_pos[0], cam_pos[1]
                            jump = True
                    if input.is_released(config['key_freecam']):
                        freecam_on = False
                        cam_pos[0], cam_pos[1] = prev_x, prev_y
                        if config['freecam_auto_center']:
                            self.axis.CamX, self.axis.CamY = 0, 0
                        prev_x, prev_y = stick_pos[0], stick_pos[1]
                        jump = True

                    if jump:
                        input.set_mouse_position(prev_x, prev_y)
                        jump = False

                    curr_x, curr_y = input.get_mouse_position()
                    delta_x = curr_x - prev_x
                    delta_y = curr_y - prev_y

                    if freecam_on:
                        self.axis.CamX += delta_x * self.axis_speed * self.damping_h
                        self.axis.CamY += delta_y * self.axis_speed * self.damping_v

                        x_percent = self.axis.CamX / AXIS_MAX
                        y_percent = self.axis.CamY / AXIS_MAX
                        screen_x = self.center_x + x_percent * (self.screen_width / 2)
                        screen_y = self.center_y + y_percent * (self.screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                        self.axis.ZoomView += wheel_step(fov(10, abs=False), input.get_wheel_delta())
                    else:
                        self.axis.Roll += delta_x * self.axis_speed * self.damping_h
                        self.axis.Pitch += delta_y * self.axis_speed * self.damping_v

                        x_percent = self.axis.Roll / AXIS_MAX
                        y_percent = self.axis.Pitch / AXIS_MAX
                        screen_x = self.center_x + x_percent * (self.screen_width / 2)
                        screen_y = self.center_y + y_percent * (self.screen_height / 2)
                        prev_x, prev_y = screen_x, screen_y

                controller = controllers.update(flight)
                if controller:
                    controller.update(
                        self.axis,
                        input,
                        SimpleNamespace(enabled=enabled, dt=delta_time, taxiing=ground_taxi),
                    )

                ctx = extension_loader.current_context
                if ctx:
                    ctx.set('mouse_pos', (prev_x, prev_y))
                    ctx.set('mouse_delta', (delta_x, delta_y))
                    ctx.set('control_active', enabled and not freecam_on)
                    ctx.set('control_steering', enabled and not freecam_on and ground_taxi)
                    ctx.set('camera_active', enabled and freecam_on)
                    ctx.set('camera_fov', axis2fov(self.axis.ZoomView))

                extension_loader.tick(delta_time)

                if enabled:
                    self.axis.Roll = check_overflow(self.axis.Roll, AXIS_MIN, AXIS_MAX)
                    self.axis.Pitch = check_overflow(self.axis.Pitch, AXIS_MIN, AXIS_MAX)
                    self.axis.Throttle = check_overflow(self.axis.Throttle, AXIS_MIN, AXIS_MAX)
                    self.axis.Rudder = check_overflow(self.axis.Rudder, AXIS_MIN, AXIS_MAX)
                    self.axis.CamX = check_overflow(self.axis.CamX, AXIS_MIN, AXIS_MAX)
                    self.axis.CamY = check_overflow(self.axis.CamY, AXIS_MIN, AXIS_MAX)
                    self.axis.ZoomView = check_overflow(self.axis.ZoomView, AXIS_MIN, AXIS_MAX)
                    self.joystick.set_all(self.axis)

                if config['show_indicator']:
                    x_val = map_to_percentage(self.axis.Roll)
                    y_val = map_to_percentage(self.axis.Pitch)
                    throttle_val = map_to_percentage(self.axis.Throttle)
                    rudder_val = map_to_percentage(self.axis.Rudder)
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

        logger.info('Creating MainWindow...')
        window = MainWindow()
        logger.info('Window created successfully')

        logger.info('Starting application event loop...')
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