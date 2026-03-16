from PySide2.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

import i18n
from data.config import ConfigData
from data.flight import FlightData
from ui.page import AbstractPage


class OptionsPage(AbstractPage):
    def __init__(self, config: ConfigData, flight: FlightData, parent=None):
        super().__init__(config, flight, parent)

        # Create the main layout
        self.optionsPageLayout = self.page_layout

        # Options area
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)

        # Show cursor option
        show_cursor_layout = QHBoxLayout()
        show_cursor_layout.setSpacing(10)
        self.showCursorLabel = QLabel()
        show_cursor_layout.addWidget(self.showCursorLabel)
        show_cursor_layout.addStretch()
        self.show_cursor = QCheckBox()
        self.show_cursor.stateChanged.connect(lambda state: self.set_config('show_cursor', bool(state)))
        show_cursor_layout.addWidget(self.show_cursor)
        options_layout.addLayout(show_cursor_layout)
        self.ui_elements.update({'show_cursor': [bool]})

        # Show hint option
        show_hint_layout = QHBoxLayout()
        show_hint_layout.setSpacing(10)
        self.showHintLabel = QLabel()
        show_hint_layout.addWidget(self.showHintLabel)
        show_hint_layout.addStretch()
        self.show_hint = QCheckBox()
        self.show_hint.stateChanged.connect(lambda state: self.set_config('show_hint', bool(state)))
        show_hint_layout.addWidget(self.show_hint)
        options_layout.addLayout(show_hint_layout)
        self.ui_elements.update({'show_hint': [bool]})

        # Show indicator option
        show_indicator_layout = QHBoxLayout()
        show_indicator_layout.setSpacing(10)
        self.showIndicatorLabel = QLabel()
        show_indicator_layout.addWidget(self.showIndicatorLabel)
        show_indicator_layout.addStretch()
        self.show_indicator = QCheckBox()
        self.show_indicator.stateChanged.connect(lambda state: self.set_config('show_indicator', bool(state)))
        show_indicator_layout.addWidget(self.show_indicator)
        options_layout.addLayout(show_indicator_layout)
        self.ui_elements.update({'show_indicator': [bool]})

        # Button mapping option
        button_mapping_layout = QHBoxLayout()
        button_mapping_layout.setSpacing(10)
        self.buttonMappingLabel = QLabel()
        button_mapping_layout.addWidget(self.buttonMappingLabel)
        button_mapping_layout.addStretch()
        self.button_mapping = QCheckBox()
        self.button_mapping.stateChanged.connect(lambda state: self.set_config('button_mapping', bool(state)))
        button_mapping_layout.addWidget(self.button_mapping)
        options_layout.addLayout(button_mapping_layout)
        self.ui_elements.update({'button_mapping': [bool]})

        # Memorize axis position option
        memorize_axis_layout = QHBoxLayout()
        memorize_axis_layout.setSpacing(10)
        self.memorizeAxisPosLabel = QLabel()
        memorize_axis_layout.addWidget(self.memorizeAxisPosLabel)
        memorize_axis_layout.addStretch()
        self.memorize_axis_pos = QCheckBox()
        self.memorize_axis_pos.stateChanged.connect(lambda state: self.set_config('memorize_axis_pos', bool(state)))
        memorize_axis_layout.addWidget(self.memorize_axis_pos)
        options_layout.addLayout(memorize_axis_layout)
        self.ui_elements.update({'memorize_axis_pos': [bool]})

        # Freecam auto center option
        freecam_auto_center_layout = QHBoxLayout()
        freecam_auto_center_layout.setSpacing(10)
        self.freecamAutoCenterLabel = QLabel()
        freecam_auto_center_layout.addWidget(self.freecamAutoCenterLabel)
        freecam_auto_center_layout.addStretch()
        self.freecam_auto_center = QCheckBox()
        self.freecam_auto_center.stateChanged.connect(
            lambda state: self.set_flight_data('freecam_auto_center', bool(state))
        )
        freecam_auto_center_layout.addWidget(self.freecam_auto_center)
        options_layout.addLayout(freecam_auto_center_layout)
        self.ui_elements.update({'freecam_auto_center': [bool]})

        options_layout.addStretch()

        self.optionsPageLayout.addLayout(options_layout)

        self.update_states()
        self.retranslate_ui()

    def retranslate_ui(self):
        self.showCursorLabel.setText(i18n.t('ShowCursor'))
        self.showHintLabel.setText(i18n.t('HintOverlay'))
        self.showIndicatorLabel.setText(i18n.t('ShowIndicator'))
        self.buttonMappingLabel.setText(i18n.t('ButtonMapping'))
        self.memorizeAxisPosLabel.setText(i18n.t('MemorizeAxisPos'))
        self.freecamAutoCenterLabel.setText(i18n.t('FreecamAutoCenter'))
