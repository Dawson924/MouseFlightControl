from typing import Any, Dict

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import i18n
from plugin import extension_loader
from plugin.runtime import Extension


class ExtensionItem(QWidget):
    def __init__(self, extension: Extension, parent=None):
        super().__init__(parent)
        self.extension = extension
        self.setStyleSheet('background-color: transparent;')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        name_label = QLabel(extension.name)
        name_label.setStyleSheet('font-weight: bold; font-size: 10pt; background-color: transparent;')
        layout.addWidget(name_label)

        id_label = QLabel(f'ID: {extension.id}')
        id_label.setStyleSheet('color: #505050; font-size: 8pt; background-color: transparent;')
        layout.addWidget(id_label)

        version_label = QLabel(f'v{extension.version}')
        version_label.setStyleSheet('color: #707070; font-size: 8pt; background-color: transparent;')
        layout.addWidget(version_label)

    def sizeHint(self):
        return self.layout().totalMinimumSize()


class ExtensionListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(200)
        self.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item):
        ext_id = item.data(Qt.UserRole)
        extension = extension_loader.get(ext_id)
        if extension:
            self.window().select_extension(extension)


class ExtensionConfigWidget(QWidget):
    config_changed = Signal(str, object)

    def __init__(self, extension: Extension, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.extension = extension
        self.config = config
        self.widgets: Dict[str, QWidget] = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        header = QLabel(self.extension.name)
        header.setObjectName('controlsTitleLabel')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('font-size: 14pt; font-weight: bold; color: #000000;')
        main_layout.addWidget(header)

        version_label = QLabel(f'Version {self.extension.version}')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet('color: #505050; font-size: 9pt;')
        main_layout.addWidget(version_label)

        main_layout.addSpacerItem(QSpacerItem(0, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.config_layout = QVBoxLayout(scroll_content)
        self.config_layout.setSpacing(10)

        for key, value in self.config.items():
            row = self.create_config_row(key, value)
            self.config_layout.addLayout(row)

        self.config_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def create_config_row(self, key: str, value: Any) -> QHBoxLayout:
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        label = QLabel(key)
        row_layout.addWidget(label)

        row_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        widget = self.create_widget(key, value)
        row_layout.addWidget(widget)
        self.widgets[key] = widget

        return row_layout

    def create_widget(self, key: str, value: Any) -> QWidget:
        if isinstance(value, bool):
            widget = QCheckBox()
            widget.setChecked(value)
            widget.stateChanged.connect(lambda checked, k=key: self.on_value_changed(k, checked))
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setMinimum(-1000000)
            widget.setMaximum(1000000)
            widget.setValue(value)
            widget.valueChanged.connect(lambda v, k=key: self.on_value_changed(k, v))
        elif isinstance(value, float):
            widget = QDoubleSpinBox()
            widget.setDecimals(3)
            widget.setSingleStep(0.001)
            widget.setMinimum(-1000000.0)
            widget.setMaximum(1000000.0)
            widget.setValue(value)
            widget.valueChanged.connect(lambda v, k=key: self.on_value_changed(k, v))
        else:
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else '')
            widget.textChanged.connect(lambda text, k=key: self.on_value_changed(k, text))

        return widget

    def on_value_changed(self, key: str, value: Any):
        self.config[key] = value
        self.config_changed.emit(self.extension.id, self.config)


class ExtensionWindow(QMainWindow):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setWindowTitle(i18n.t('Extensions'))
        self.setMinimumSize(600, 400)
        self.init_style()
        self.init_ui()
        self.populate_extensions()

    def init_style(self):
        self.setStyleSheet(self.parent().get_stylesheet())

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel(i18n.t('Extensions'))
        list_label.setStyleSheet('font-weight: bold; font-size: 10pt;')
        left_layout.addWidget(list_label)

        self.extension_list = ExtensionListWidget()
        left_layout.addWidget(self.extension_list)

        main_layout.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.config_container = QWidget()
        self.config_layout = QVBoxLayout(self.config_container)
        self.config_layout.setContentsMargins(0, 0, 0, 0)

        self.empty_label = QLabel(i18n.t('SelectExtension'))
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet('color: #707070; font-size: 10pt;')
        self.config_layout.addWidget(self.empty_label)

        right_layout.addWidget(self.config_container)

        main_layout.addWidget(right_panel, 1)

    def populate_extensions(self):
        self.extension_list.clear()
        for ext in extension_loader.extensions:
            item = QListWidgetItem(self.extension_list)
            item.setData(Qt.UserRole, ext.id)
            widget = ExtensionItem(ext)
            item.setSizeHint(widget.sizeHint())
            self.extension_list.setItemWidget(item, widget)

    def select_extension(self, extension: Extension):
        while self.config_layout.count():
            child = self.config_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        runtime = extension_loader.get_context(extension.id)
        if runtime:
            config = runtime.load_settings(extension.id)
        else:
            config = {}
        if not config:
            config = extension.get_default_config()

        self.current_config_widget = ExtensionConfigWidget(extension, config, self)
        self.current_config_widget.config_changed.connect(self.on_config_changed)
        self.config_layout.addWidget(self.current_config_widget)

    def on_config_changed(self, ext_id: str, config: Dict[str, Any]):
        runtime = extension_loader.get_context(ext_id)
        if runtime:
            runtime.save_settings(ext_id, config)