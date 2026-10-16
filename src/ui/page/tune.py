from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
)

import i18n
from common.axis import CONTROL_AXES, ControlAxis
from ui.page.abstract import AbstractPage
from ui.window.axis import JoyAxisWindow


class TunePage(AbstractPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tuneLayout = self.page_layout

        self._axis_labels = {}
        self._axis_buttons = {}

        for c_axis in CONTROL_AXES:
            axis_layout = QHBoxLayout()
            axis_layout.setSpacing(10)

            label = QLabel()
            button = QPushButton()
            button.clicked.connect(lambda *args, axis=c_axis: self.open_axis_window(axis))

            self._axis_labels[c_axis] = label
            self._axis_buttons[c_axis] = button

            axis_layout.addWidget(label)
            axis_layout.addStretch()
            axis_layout.addWidget(button)

            self.tuneLayout.addLayout(axis_layout)

        self.retranslate_ui()

        self.tuneLayout.addStretch()

    def retranslate_ui(self):
        for axis_name in CONTROL_AXES:
            self._axis_labels[axis_name].setText(i18n.t('JoyAxis', axis=axis_name))
            self._axis_buttons[axis_name].setText(i18n.t('Modify'))

    def update_ui(self):
        pass

    def open_axis_window(self, axis: ControlAxis):
        window = JoyAxisWindow(axis, self.flight, self)
        window.show()
