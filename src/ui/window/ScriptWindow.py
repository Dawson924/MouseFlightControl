from typing import Any, Dict, List, Tuple

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from type.script import ScriptModule


class ScriptWindow(QMainWindow):
    def __init__(self, script: ScriptModule, config: Dict, parent: QMainWindow):
        super().__init__(parent)
        self.setWindowTitle(parent.tr('OptionsTitle'))
        self.init_style()

        self.script = script
        self.config = config
        self.widget = self.init_widget()
        self.setCentralWidget(self.widget)
        self.create_options(script.options)

    def init_style(self):
        self.setMinimumWidth(300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F0F0;
                font-size: 9pt;
            }
            QWidget {
                background-color: #F0F0F0;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                background-color: #E1E1E1;
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QPushButton:pressed {
                background-color: #C0C0C0;
                border: 1px solid #707070;
            }
            QSlider::groove:horizontal {
                border: 1px solid #A0A0A0;
                height: 6px;
                background: #D0D0D0;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #E1E1E1;
                border: 1px solid #707070;
                width: 16px;
                margin: -4px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal:hover {
                background: #F0F0F0;
            }
            QSlider::add-page:horizontal {
                background: #B0B0B0;
            }
            QSlider::sub-page:horizontal {
                background: #0078D7;
            }
            QLineEdit {
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: 100px;
                max-width: 100px;
            }
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: 100px;
                max-width: 100px;
            }
            QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background: transparent;
                border: none;
                width: 16px;
            }
            QSpinBox::up-arrow {
                image: url(assets/up_arrow.svg);
                width: 16px;
                height: 16px;
            }
            QSpinBox::down-arrow {
                image: url(assets/down_arrow.svg);
                width: 16px;
                height: 16px;
            }
            #controllerComboBox {
                border: 1px solid #A0A0A0;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: 120px;
            }
            #controllerComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #A0A0A0;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            #controllerComboBox::down-arrow {
                image: url(assets/down_arrow.svg);
                width: 16px;
                height: 16px;
            }
            #controllerComboBox QAbstractItemView {
                border: 1px solid #A0A0A0;
                background: white;
                selection-background-color: #E1E1E1;
            }
            .title-label {
                font-size: 14pt;
                font-weight: bold;
                color: #000000;
                text-align: center;
            }
            .desc-label {
                color: #505050;
                font-size: 9pt;
                word-wrap: true;
            }
        """)

    def init_widget(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(10)

        controls_title = QLabel(self.script.name)
        controls_title.setObjectName('controlsTitleLabel')
        controls_title.setAlignment(Qt.AlignCenter)
        controls_title.setStyleSheet(
            'font-size: 14pt; font-weight: bold; color: #000000;'
        )
        main_layout.addWidget(controls_title)

        self.config_layout = QVBoxLayout()
        self.config_layout.setSpacing(10)
        main_layout.addLayout(self.config_layout)

        main_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)
        )

        main_layout.addSpacerItem(
            QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        return central_widget

    def set_config(self, key: str, value: Any):
        # TODO 类型检查和合法性校验
        self.config[key] = value

    def add_config_row(
        self, name: str, label: str, widget_type: int, value: Any
    ) -> QHBoxLayout:
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        label = QLabel(label)
        row_layout.addWidget(label)

        row_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        if widget_type == 'bool':
            widget = QCheckBox()
            widget.setChecked(value if isinstance(value, bool) else False)
            widget.stateChanged.connect(
                lambda checked, key=name: self.set_config(key, checked)
            )
        elif widget_type == 'string':
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else '')
            widget.textChanged.connect(
                lambda text, key=name: self.set_config(key, text)
            )
        elif widget_type == 'int':
            widget = QSpinBox()
            widget.setMinimum(-1000000)
            widget.setMaximum(1000000)
            widget.setValue(value)
            widget.valueChanged.connect(
                lambda value, key=name: self.set_config(key, value)
            )
        elif widget_type == 'uint':
            widget = QSpinBox()
            widget.setMinimum(0)
            widget.setMaximum(1000000)
            widget.setValue(value)
            widget.valueChanged.connect(
                lambda value, key=name: self.set_config(key, value)
            )
        elif widget_type == 'float':
            widget = QDoubleSpinBox()
            widget.setDecimals(3)
            widget.setSingleStep(0.001)
            widget.setMinimum(0.0)
            widget.setMaximum(100.0)
            widget.setValue(value)
            widget.valueChanged.connect(
                lambda value, key=name: self.set_config(key, value)
            )
        else:
            widget = QLabel('Invalid')
            widget.setStyleSheet('color: red;')

        row_layout.addWidget(widget)
        return row_layout

    def create_options(self, list: List[Tuple[str, str, Any]]):
        for option in list:
            if len(option) != 3:
                continue
            name, type, default = option
            if hasattr(self.script, 'i18n'):
                language = (
                    self.parent().language
                    if hasattr(self.parent(), 'language')
                    else 'en_US'
                )
                label = self.script.i18n.get(name, {}).get(language, name)
            else:
                label = name
            row_layout = self.add_config_row(
                name,
                label,
                type,
                self.config[name] if name in self.config else default,
            )
            self.config_layout.addLayout(row_layout)
