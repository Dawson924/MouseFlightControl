import os

from loguru import logger
from PySide2.QtCore import QSize, Qt, QTimer, Signal
from PySide2.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPixmap
from PySide2.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import i18n
from connect.DCS import DCSConnect
from connect.flight import FlightConnect
from connect.install import install, is_installed
from connect.module import FlightModules, FlightSim
from connect.MSFS import MSFSConnect
from data.config import Config
from data.flight import FlightInput
from lib.container import store
from lib.screen import ScreenGeometry
from ui.factory import WidgetFactory
from ui.widgets import ComboBox

from . import AbstractPage


class ImagePixmap(QLabel):
    def __init__(self, parent=None, radius=4, opacity=1, gradient=0):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = QPixmap()
        self._radius = radius
        self._opacity = opacity
        self._alpha = gradient

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()

    def setGradientAlpha(self, alpha):
        self._alpha = alpha
        self.update()

    def paintEvent(self, event):
        if self._pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.contentsRect()

        scaled_pixmap = self._pixmap.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        x = (rect.width() - scaled_pixmap.width()) // 2
        y = (rect.height() - scaled_pixmap.height()) // 2

        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        painter.setClipPath(path)

        painter.drawPixmap(x, y, scaled_pixmap)

        # Background overlay
        overlay_path = QPainterPath()
        overlay_path.addRoundedRect(rect, self._radius, self._radius)
        painter.fillPath(overlay_path, QColor(0, 0, 0, 255 * (1 - self._opacity)))

        # Background gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(1, QColor(0, 0, 0, self._alpha))
        painter.fillPath(overlay_path, gradient)


class ImageCard(QFrame):
    clicked = Signal(str)

    def __init__(self, id, text, parent=None):
        super().__init__(parent)
        self.id = id
        self.text = text

        self.setStyleSheet("""
            ImageCard {
                background-color: #f8f9fa;
            }
            ImageCard:hover {
                background-color: #eef2f7;
            }
        """)

        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.image_container = QWidget(self)
        self.image_container.setMinimumHeight(130)
        self.image_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_image_label = ImagePixmap(self.image_container, radius=8, opacity=1, gradient=100)
        self.bg_image_label.setObjectName('bgImageLabel')
        self.bg_image_label.setMinimumHeight(130)
        container_layout.addWidget(self.bg_image_label)

        self.name_label = QLabel(text, self.image_container)
        self.name_label.setObjectName('nameLabel')
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        layout.addWidget(self.image_container)

        self.setCursor(Qt.PointingHandCursor)

        self._has_image = False
        self._current_alpha = 100
        self._target_alpha = 150
        self._transition_timer = QTimer(self)
        self._transition_timer.setInterval(16)
        self._transition_timer.timeout.connect(self._on_transition_tick)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.image_container.width()
        h = self.name_label.sizeHint().height()
        container_h = self.image_container.height()
        self.name_label.setGeometry(0, container_h - h, w, h)

    def _start_transition(self, target_alpha):
        self._target_alpha = target_alpha
        if not self._transition_timer.isActive():
            self._transition_timer.start()

    def _on_transition_tick(self):
        step = 8
        if self._current_alpha < self._target_alpha:
            self._current_alpha = min(self._current_alpha + step, self._target_alpha)
        elif self._current_alpha > self._target_alpha:
            self._current_alpha = max(self._current_alpha - step, self._target_alpha)
        self.bg_image_label.setGradientAlpha(self._current_alpha)
        if self._current_alpha == self._target_alpha:
            self._transition_timer.stop()

    def enterEvent(self, event):
        if self._has_image:
            self._start_transition(150)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._has_image:
            self._start_transition(100)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.id)
        super().mousePressEvent(event)

    def set_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(QSize(200, 260), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.bg_image_label.setPixmap(scaled_pixmap)

            self._has_image = True
        else:
            self._has_image = False
            self.bg_image_label.setStyleSheet("""
                ImageCard #bgImageLabel {
                    background-color: #121212;
                    border-radius: 8px;
                }
            """)

        self.name_label.setStyleSheet("""
            ImageCard #nameLabel {
                font-size: 14px;
                font-weight: 500;
                color: #d0d0d0;
                background-color: transparent;
                padding: 18px 8px 6px 8px;
            }
        """)


SIMULATORS = {
    FlightSim.DCS: {'name': FlightSim.DCS.full_name, 'image_path': 'assets/Default.jpg'},
    FlightSim.FS2020: {'name': FlightSim.FS2020.full_name, 'image_path': 'assets/Default.jpg'},
}


JET_PLANE_INPUTS = ['camera_fov', 'thrust_speed', 'throttle_increase', 'throttle_decrease']

HELICOPTER_INPUTS = [
    'camera_fov',
    'thrust_speed',
    'rudder_speed',
    'collective_increase',
    'collective_decrease',
    'rudder_left',
    'rudder_right',
    'rudder_center',
    'collective_minimum',
    'collective_maximum',
]

PISTON_PLANE_INPUTS = [
    'camera_fov',
    'thrust_speed',
    'throttle_increase',
    'throttle_decrease',
    'rudder_left',
    'rudder_right',
]


class ConnectPage(AbstractPage):
    def __init__(self, win: ScreenGeometry, config: Config, flight: FlightInput, modules: FlightModules, parent=None):
        super().__init__(win, config, flight, parent)

        self._image_cache = {}
        self._last_image_path = None
        self._no_data = False
        self._in_spectator = False
        self._current_page = 1
        self._current_mode = 0
        self._fields_per_page = 8
        self._total_pages = 1

        self.mod_data: FlightModules = {}
        self.connector: FlightConnect = store.get('connector')
        self.msg_box = store.get('message_box')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_connect)
        self.timer.start(300)

        self.pageLayout = self.page_layout
        self.pageLayout.setSpacing(10)
        self.pageLayout.setContentsMargins(0, 0, 0, 0)

        # SIMULATOR DROPDOWN
        self.headerLayout = QHBoxLayout()
        self.headerLayout.setSpacing(8)
        self.simulatorLabel = QLabel()
        self.simulatorLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
            }
        """)
        self.headerLayout.addWidget(self.simulatorLabel)
        self.simulatorDropdown = ComboBox()
        self.simulatorDropdown.currentIndexChanged.connect(self.simulator_changed)
        self.headerLayout.addWidget(self.simulatorDropdown)
        self.pageLayout.addLayout(self.headerLayout)

        # MODULE LIST PANEL
        self.module_list = QScrollArea(self)
        self.module_list.setWidgetResizable(True)
        self.module_list.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c4cc;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #909399;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 4, 0)
        self.list_layout.setAlignment(Qt.AlignTop)

        # MODULE CONFIGURATION PANEL
        self.module_panel = QWidget()
        self.module_panel_layout = QVBoxLayout(self.module_panel)
        self.module_panel_layout.setContentsMargins(0, 0, 4, 0)
        self.module_panel_layout.setAlignment(Qt.AlignTop)
        self.module_panel_layout.setSpacing(8)

        image_section = QWidget()
        image_layout = QGridLayout(image_section)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        self.image_label = ImagePixmap(radius=8, opacity=0.8)
        self.image_label.setMinimumHeight(80)
        self.image_label.setMaximumHeight(120)
        image_layout.addWidget(self.image_label, 0, 0)

        self.title_container = QWidget()
        self.title_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        self.title_container.setFixedHeight(50)
        self.title_layout = QVBoxLayout(self.title_container)
        self.title_layout.setContentsMargins(8, 6, 6, 6)
        self.title_layout.setSpacing(0)

        self.sim_label = QLabel()
        self.sim_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                background: transparent;
            }
        """)
        self.title_layout.addWidget(self.sim_label)

        self.module_label = QLabel()
        self.module_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-weight: 500;
                color: #d4d4d4;
                background: transparent;
            }
        """)
        self.title_layout.addWidget(self.module_label)

        image_layout.addWidget(self.title_container, 0, 0, Qt.AlignTop | Qt.AlignLeft)

        flight_panel = QWidget()
        flight_panel.setObjectName('flightPanel')
        flight_panel.setStyleSheet("""
            #flightPanel {
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
            QWidget {
                background-color: #f8f9fa;
            }
        """)
        self.flight_layout = QVBoxLayout(flight_panel)
        self.flight_layout.setContentsMargins(10, 10, 10, 10)

        self.returnLabel = QLabel()
        self.returnLabel.setText(i18n.t('BackToModules'))
        self.returnLabel.setObjectName('returnLabel')
        self.returnLabel.setAlignment(Qt.AlignCenter)
        self.returnLabel.setStyleSheet("""
            #returnLabel {
                font-size: 11px;
                font-weight: 400;
                color: dimgray;
                background-color: transparent;
                border-radius: 4px;
                padding: 6px 8px;
            }
            #returnLabel:hover {
                background-color: #e0e0e0;
            }
        """)
        size_policy = self.returnLabel.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Minimum)
        self.returnLabel.setSizePolicy(size_policy)
        self.returnLabel.adjustSize()
        self.returnLabel.setCursor(Qt.PointingHandCursor)
        self.returnLabel.mousePressEvent = self.label_clicked

        self.page_navigation = QWidget()
        self.page_navigation.setStyleSheet('background-color: transparent;')
        nav_layout = QHBoxLayout(self.page_navigation)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(10)
        self.prev_button = QLabel('<')
        self.prev_button.setAlignment(Qt.AlignCenter)
        self.prev_button.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #606266;
                min-width: 24px;
                padding: 4px 8px;
            }
            QLabel:hover {
                color: #409EFF;
                background-color: #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.mousePressEvent = self._prev_page
        self.page_label = QLabel('1')
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #606266;
                min-width: 30px;
            }
        """)
        self.next_button = QLabel('>')
        self.next_button.setAlignment(Qt.AlignCenter)
        self.next_button.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #606266;
                min-width: 24px;
                padding: 4px 8px;
            }
            QLabel:hover {
                color: #409EFF;
                background-color: #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.mousePressEvent = self._next_page
        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_button)
        nav_layout.addStretch()

        self.module_panel_layout.addWidget(image_section)
        self.module_panel_layout.addWidget(flight_panel, 1)
        self.module_panel_layout.addWidget(self.page_navigation)
        self.module_panel_layout.addWidget(self.returnLabel, 0, Qt.AlignCenter)

        self.module_list.setWidget(self.list_container)
        self.module_list.hide()

        self.pageLayout.addWidget(self.module_list)
        self.pageLayout.addWidget(self.module_panel)

        self._module_list = {}

        self.init_modules(modules)
        self.init_connect()
        self.init_ui()
        self.retranslate_ui()

    def _create_module_cards(self, simulator):
        grouped_modules = {}

        for mod_id, module in self.mod_data.items():
            if module['platform'] != simulator:
                continue

            image_path = module['image_path']
            name = module['name']
            key = (image_path, name)

            if key not in grouped_modules:
                grouped_modules[key] = {'ids': [], 'module': module}
            grouped_modules[key]['ids'].append(mod_id)

        for (image_path, name), data in grouped_modules.items():
            ids = data['ids']
            module = data['module']

            display_name = f'{name} ({len(ids)})' if len(ids) > 1 else name
            primary_id = ids[0]

            if primary_id not in self._module_list:
                card = ImageCard(primary_id, display_name)
                card.clicked.connect(lambda key=primary_id: self.module_clicked(key))
                self._module_list[primary_id] = card
                self.list_layout.addWidget(card)
                card._image_path = image_path
                card.set_background_image(image_path)
                card._model_ids = ids
            else:
                card = self._module_list[primary_id]

    def init_modules(self, mod_data: FlightModules):
        self.mod_data = mod_data
        self._model = self.flight['Connect']['model']
        simulator = self.flight['Connect'].get('simulator')
        if simulator:
            self._simulator = FlightSim(simulator)
        else:
            self._simulator = self.get_platform(self._model)
        self.check_dependencies()
        for simulator in SIMULATORS.keys():
            self._create_module_cards(simulator)

    def init_ui(self):
        sim_list = [(simid, detail['name']) for simid, detail in SIMULATORS.items()]
        self.populate_simulators(sim_list)

        if not self._simulator:
            self._simulator = sim_list[0][0]
            self.simulatorDropdown.setCurrentIndex(0)

        if self.config['auto_connect'] and self._model:
            self._set_model(None)

        self.render_modules(self._simulator)
        self.update_ui()

    def init_connect(self):
        try:
            logger.info('Attempting to connect...')

            simulator = self._simulator
            if simulator == FlightSim.DCS:
                self.connector = DCSConnect()
            elif simulator == FlightSim.FS2020:
                self.connector = MSFSConnect()
            else:
                return

            store.set('connector', self.connector)
            self.connector.connect()

        except Exception as e:
            logger.exception(str(e))

    def populate_simulators(self, simulators):
        self.simulatorDropdown.blockSignals(True)
        self.simulatorDropdown.clear()
        for simid, name in simulators:
            self.simulatorDropdown.addItem(name, simid)
        self.simulatorDropdown.blockSignals(False)

    def render_modules(self, simulator):
        grouped_modules = {}

        for mod_id, module in self.mod_data.items():
            if module['platform'] != simulator:
                continue

            image_path = module['image_path']
            name = module['name']
            key = (image_path, name)

            if key not in grouped_modules:
                grouped_modules[key] = {'ids': [], 'module': module}
            grouped_modules[key]['ids'].append(mod_id)

        visible_ids = set()
        for (image_path, name), data in grouped_modules.items():
            ids = data['ids']
            module = data['module']

            display_name = f'{name} ({len(ids)})' if len(ids) > 1 else name
            primary_id = ids[0]
            visible_ids.add(primary_id)

            if primary_id in self._module_list:
                card = self._module_list[primary_id]
                card.text = display_name
                card._model_ids = ids
                card.name_label.setText(display_name)

        for card_id, card in self._module_list.items():
            module = self.mod_data.get(card_id)
            card.setVisible(card_id in visible_ids)

        self._simulator = simulator

    def check_dependencies(self):
        simulator = self._simulator

        if simulator is None:
            return

        if simulator not in SIMULATORS:
            logger.warning(f'Unknown simulator: {simulator}')
            return

        if is_installed(simulator):
            logger.info(f'FlightConnect installed for {simulator.full_name}')
            return

        result = self.msg_box.question(
            title=i18n.t('InstallationRequired'),
            text=i18n.t('FlightConnectNotInstalled'),
            detail=i18n.t('InstallFlightConnectPrompt', simulator=simulator.full_name),
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.Yes,
        )

        if result == QMessageBox.Yes:
            installed_path = install(simulator)

            if installed_path:
                self.msg_box.info(
                    title=i18n.t('InstallationComplete'),
                    text=i18n.t('InstallationSuccess'),
                    detail=f'{installed_path}',
                )
            else:
                self.msg_box.error(
                    title=i18n.t('InstallationFailed'),
                    text=i18n.t('NoUserDataPathFound', simulator=simulator.full_name),
                )

    def _set_model(self, mod_id=None):
        if not mod_id:
            self.flight['Connect']['model'] = ''
            self._model = None
            logger.debug('MODEL: None')
            return

        module = self.mod_data.get(mod_id)
        if not module:
            logger.warning(f'{mod_id} NOT FOUND')
            return

        self.flight['Connect']['model'] = mod_id
        self.flight['Connect']['simulator'] = module['platform'].value
        self.flight['Input'] = {
            k: module['data'][k] if k in module['data'] else v for k, v in self.flight['Input'].items()
        }

        self._model = mod_id
        self._simulator = module['platform']

        logger.debug(f'MODEL: {mod_id}')

    def _set_model_label(self, text, active=False):
        if active:
            self.module_label.setText(text)
            self.module_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 500;
                    color: #d4d4d4;
                    background: transparent;
                }
            """)
        else:
            self.module_label.setText(text)
            self.module_label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    font-weight: 500;
                    color: #d4d4d4;
                    background: transparent;
                }
            """)

    def _set_model_image(self, image_path):
        if not image_path or not os.path.exists(image_path):
            image_path = self._get_default_image()

        if image_path == self._last_image_path:
            return

        self._last_image_path = image_path

        cache_key = image_path

        if cache_key in self._image_cache:
            scaled_pixmap = self._image_cache[cache_key]
        else:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.image_label.setPixmap(None)
                self.image_label.setStyleSheet("""
                    ImageLabel {
                        background-color: #f8f9fa;
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                    }
                """)
                return

            width = self.image_label.width()
            height = self.image_label.height()
            scaled_pixmap = pixmap.scaled(
                width,
                height,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            self._image_cache[cache_key] = scaled_pixmap

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setScaledContents(True)

    def _set_module_content(self, mod_id, connecting=False):
        if self._simulator:
            self.sim_label.setText(SIMULATORS[self._simulator]['name'])

        if connecting:
            self._toggle_panel(True)
            self._set_model_label('NO CONNECTION')
            self._set_model_image(None)
            self._render_options(0)
            self.page_navigation.hide()
            return

        module = self.mod_data.get(mod_id)
        if module:
            display_name = module['name'] if not module['is_grouped'] else mod_id
            self._set_model_label(display_name, True)
            image_path = module.get('image_path')
            self._set_model_image(image_path)
            self._toggle_panel(True)
        else:
            self._toggle_panel(False)

    def _render_options(self, mode):
        self._current_page = 1
        self._current_mode = mode
        self._clear_options()

        _fields = self._get_flight_options(mode)

        if not _fields:
            label = QLabel('NO MODULE SELECTED')
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    font-weight: 400;
                    color: #888888;
                }
            """)
            self.flight_layout.insertWidget(0, label)
            return

        input_spec = FlightInput.SPEC['Input']
        all_fields = []
        for field_name in _fields:
            if field_name not in input_spec:
                continue
            field_spec = input_spec[field_name]
            if 'widget' not in field_spec:
                continue
            all_fields.append((field_name, field_spec))

        self._total_pages = max(1, (len(all_fields) + self._fields_per_page - 1) // self._fields_per_page)
        self._update_pagination()

        start_idx = (self._current_page - 1) * self._fields_per_page
        end_idx = start_idx + self._fields_per_page
        page_fields = all_fields[start_idx:end_idx]

        spec_group = dict(page_fields)

        WidgetFactory.populate_from_spec(self.flight_layout, spec_group, self.set_flight_data, self)

        for field_name, field_spec in spec_group.items():
            self.ui_elements.update({field_name: [field_spec['type']]})

        WidgetFactory.retranslate_from_spec(spec_group, self)
        WidgetFactory.add_stretch(self.flight_layout)

    def _update_pagination(self):
        self.page_label.setText(f'{self._current_page}/{self._total_pages}')
        is_pagination_needed = self._total_pages > 1
        self.page_navigation.setVisible(is_pagination_needed)
        if is_pagination_needed:
            self.prev_button.setEnabled(self._current_page > 1)
            self.next_button.setEnabled(self._current_page < self._total_pages)

    def _prev_page(self, event=None):
        if self._current_page > 1:
            self._current_page -= 1
            self._render_current_page()

    def _next_page(self, event=None):
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._render_current_page()

    def _render_current_page(self):
        mode = getattr(self, '_current_mode', 0)
        _fields = self._get_flight_options(mode)

        if not _fields:
            return

        input_spec = FlightInput.SPEC['Input']
        all_fields = []
        for field_name in _fields:
            if field_name not in input_spec:
                continue
            field_spec = input_spec[field_name]
            if 'widget' not in field_spec:
                continue
            all_fields.append((field_name, field_spec))

        start_idx = (self._current_page - 1) * self._fields_per_page
        end_idx = start_idx + self._fields_per_page
        page_fields = all_fields[start_idx:end_idx]

        self._clear_option_widgets()

        spec_group = dict(page_fields)

        WidgetFactory.populate_from_spec(self.flight_layout, spec_group, self.set_flight_data, self)

        for field_name, field_spec in spec_group.items():
            self.ui_elements.update({field_name: [field_spec['type']]})

        WidgetFactory.retranslate_from_spec(spec_group, self)
        WidgetFactory.add_stretch(self.flight_layout)

        self._update_pagination()
        self.update_states()

    def _clear_option_widgets(self):
        while self.flight_layout.count():
            item = self.flight_layout.takeAt(0)
            if item.widget():
                if item.widget() == self.page_navigation:
                    continue
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

        self.ui_elements.clear()

    def _clear_options(self):
        while self.flight_layout.count():
            item = self.flight_layout.takeAt(0)
            if item.widget():
                if item.widget() == self.page_navigation:
                    continue
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

        self.ui_elements.clear()

    def _delete_layout(self, layout):
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

        layout.deleteLater()

    def _get_default_image(self) -> str:
        if self._simulator:
            return SIMULATORS[self._simulator]['image_path']
        return 'assets/Default.jpg'

    def _get_flight_options(self, flight_mode):
        if flight_mode == 1:
            return JET_PLANE_INPUTS
        elif flight_mode == 2:
            return HELICOPTER_INPUTS
        elif flight_mode == 3:
            return PISTON_PLANE_INPUTS
        return []

    def _set_module(self, mod_id):
        self._set_model(mod_id)
        self._set_module_content(mod_id, self.config['auto_connect'] and mod_id is None)
        if self.connector:
            self.connector.emit('model_changed', mod_id)

    def _toggle_panel(self, visible: bool = True):
        if visible:
            self.simulatorLabel.hide()
            self.simulatorDropdown.hide()
            self.module_list.hide()
            self.module_panel.show()
        else:
            self.simulatorLabel.show()
            self.simulatorDropdown.show()
            self.module_list.show()
            self.module_panel.hide()

    def update_connect(self):
        auto_connect = self.config['auto_connect']
        if not auto_connect:
            return

        data = self.connector.get_data()
        if not data:
            if self._no_data:
                return

            logger.debug('FLIGHTCONNECT: No data received from connector')
            self._set_module(None)
            self._no_data = True
            return

        elif data.model == 'Spectator':
            if self._in_spectator:
                return

            logger.debug('FLIGHTCONNECT: Player is in Spectator slot')
            self._set_module(None)
            self._in_spectator = True
            return

        elif data.model != self._model:
            logger.debug(f'FLIGHTCONNECT: {data.model} received from {self._simulator}')
            self._set_module(data.model)
            self._toggle_panel(True)

            module = self.mod_data.get(data.model)
            if module:
                self._render_options(module.get('aircraft_type', 0))
            else:
                self._render_options(0)

            self.update_states()

        self._no_data = False
        self._in_spectator = False

    def simulator_changed(self):
        simulator = self.simulatorDropdown.currentData()
        if simulator is not None:
            self._simulator = simulator
            self.flight['Connect']['simulator'] = simulator
            self.render_modules(simulator)
            self._toggle_panel(False)

        logger.debug(f'SIMULATOR: {simulator}')

    def module_clicked(self, mod_id):
        self._set_module(mod_id)
        self.update_ui()

    def label_clicked(self, _):
        self.config['auto_connect'] = False
        self._no_data = False
        self._set_module(None)

    def get_platform(self, module_id) -> FlightSim:
        module = self.mod_data.get(module_id)
        return module['platform'] if module else None

    def update_ui(self):
        model = self._model
        simulator = self._simulator

        if self.config['auto_connect']:
            self._toggle_panel(True)

        elif model:
            if not simulator:
                simulator = self.get_platform(model)

            self._set_module_content(model)
            module = self.mod_data.get(model)
            if module:
                self._render_options(module.get('aircraft_type', 0))
            else:
                self._render_options(0)

            self.update_states()

        else:
            self._toggle_panel(False)

        self.simulatorDropdown.blockSignals(True)
        if simulator:
            index = self.simulatorDropdown.findData(FlightSim(simulator))
            if index >= 0:
                self.simulatorDropdown.setCurrentIndex(index)
        self.simulatorDropdown.blockSignals(False)

    def retranslate_ui(self):
        self.simulatorLabel.setText(i18n.t('FlightSim'))
        self.returnLabel.setText(i18n.t('BackToModules'))

        flight_mode = self.flight.get('flight_mode', 0)
        option_fields = self._get_flight_options(flight_mode)

        if not option_fields:
            return

        spec_group = {}
        input_spec = FlightInput.SPEC['Input']

        for option_name in option_fields:
            if option_name in input_spec and 'i18n' in input_spec[option_name]:
                spec_group[option_name] = {'i18n': input_spec[option_name]['i18n']}

        WidgetFactory.retranslate_from_spec(spec_group, self)
