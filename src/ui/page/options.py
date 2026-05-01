from PySide2.QtWidgets import QVBoxLayout

from data.config import Config
from data.flight import FlightInput
from lib.screen import ScreenGeometry
from ui.factory import WidgetFactory
from ui.page import AbstractPage


class OptionsPage(AbstractPage):
    def __init__(self, win: ScreenGeometry, config: Config, flight: FlightInput, parent=None):
        super().__init__(win, config, flight, parent)

        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(8)
        self.page_layout.addLayout(self.options_layout)

        self._widgets = WidgetFactory.populate_from_spec(
            self.options_layout, Config.SPEC['Options'], self.set_config, self
        )

        for field_name in self._widgets:
            self.ui_elements.update({field_name: [Config.SPEC['Options'][field_name]['type']]})

        WidgetFactory.add_stretch(self.options_layout)

        self.update_states()
        self.retranslate_ui()

    def retranslate_ui(self):
        WidgetFactory.retranslate_from_spec(Config.SPEC['Options'], self)

    def update_ui(self):
        self.update_states()
