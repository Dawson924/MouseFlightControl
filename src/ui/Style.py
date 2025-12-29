STYLE_LIGHT = """
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
        """
