# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(350, 350)
        MainWindow.setStyleSheet(u"\n"
"                QMainWindow {\n"
"                background-color: #F0F0F0;\n"
"                font-size: 9pt;\n"
"                }\n"
"                QWidget {\n"
"                background-color: #F0F0F0;\n"
"                }\n"
"                QLabel {\n"
"                color: #000000;\n"
"                }\n"
"                QPushButton {\n"
"                background-color: #E1E1E1;\n"
"                border: 1px solid #A0A0A0;\n"
"                border-radius: 3px;\n"
"                padding: 5px;\n"
"                min-width: 80px;\n"
"                }\n"
"                QPushButton:hover {\n"
"                background-color: #D0D0D0;\n"
"                }\n"
"                QPushButton:pressed {\n"
"                background-color: #C0C0C0;\n"
"                border: 1px solid #707070;\n"
"                }\n"
"                QSlider::groove:horizontal {\n"
"                border: 1px solid #A0A0A0;\n"
"                height: 6px;\n"
"                background: #D0D0D0;\n"
""
                        "                margin: 2px 0;\n"
"                }\n"
"                QSlider::handle:horizontal {\n"
"                background: #E1E1E1;\n"
"                border: 1px solid #707070;\n"
"                width: 16px;\n"
"                margin: -4px 0;\n"
"                border-radius: 3px;\n"
"                }\n"
"                QSlider::handle:horizontal:hover {\n"
"                background: #F0F0F0;\n"
"                }\n"
"                QSlider::add-page:horizontal {\n"
"                background: #B0B0B0;\n"
"                }\n"
"                QSlider::sub-page:horizontal {\n"
"                background: #0078D7;\n"
"                }\n"
"                QLineEdit {\n"
"                border: 1px solid #A0A0A0;\n"
"                border-radius: 3px;\n"
"                padding: 4px;\n"
"                background: white;\n"
"                min-width: 100px;\n"
"                max-width: 100px;\n"
"                }\n"
"                QSpinBox {\n"
"                border: 1px solid"
                        " #A0A0A0;\n"
"                border-radius: 3px;\n"
"                padding: 4px;\n"
"                background: white;\n"
"                min-width: 100px;\n"
"                max-width: 100px;\n"
"                }\n"
"                QSpinBox::up-button, QSpinBox::down-button {\n"
"                background: transparent;\n"
"                border: none;\n"
"                width: 16px;\n"
"                }\n"
"                QSpinBox::up-arrow {\n"
"                image: url(assets/up_arrow.svg); /* \u81ea\u5b9a\u4e49\u5411\u4e0a\u7bad\u5934 */\n"
"                width: 16px;\n"
"                height: 16px;\n"
"                }\n"
"                QSpinBox::down-arrow {\n"
"                image: url(assets/down_arrow.svg); /* \u81ea\u5b9a\u4e49\u5411\u4e0b\u7bad\u5934 */\n"
"                width: 16px;\n"
"                height: 16px;\n"
"                }\n"
"                #controllerComboBox {\n"
"                border: 1px solid #A0A0A0;\n"
"                border-radius: 3px;\n"
"    "
                        "            padding: 4px;\n"
"                background: white;\n"
"                min-width: 120px;\n"
"                }\n"
"                #controllerComboBox::drop-down {\n"
"                subcontrol-origin: padding;\n"
"                subcontrol-position: top right;\n"
"                width: 20px;\n"
"                border-left-width: 1px;\n"
"                border-left-color: #A0A0A0;\n"
"                border-left-style: solid;\n"
"                border-top-right-radius: 3px;\n"
"                border-bottom-right-radius: 3px;\n"
"                }\n"
"                #controllerComboBox::down-arrow {\n"
"                image: url(assets/down_arrow.svg);\n"
"                width: 16px;\n"
"                height: 16px;\n"
"                }\n"
"                #controllerComboBox QAbstractItemView {\n"
"                border: 1px solid #A0A0A0;\n"
"                background: white;\n"
"                selection-background-color: #E1E1E1;\n"
"                }\n"
"            ")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 10, 15, 15)
        self.controlsTitleLabel = QLabel(self.centralWidget)
        self.controlsTitleLabel.setObjectName(u"controlsTitleLabel")
        self.controlsTitleLabel.setAlignment(Qt.AlignCenter)
        self.controlsTitleLabel.setStyleSheet(u"font-size: 14pt; font-weight: bold;\n"
"                                color: #000000;")

        self.verticalLayout.addWidget(self.controlsTitleLabel)

        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setSpacing(5)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.speedLabel = QLabel(self.centralWidget)
        self.speedLabel.setObjectName(u"speedLabel")
        self.speedLabel.setStyleSheet(u"color: #000000;")

        self.vboxLayout.addWidget(self.speedLabel)

        self.mouseSpeedSlider = QSlider(self.centralWidget)
        self.mouseSpeedSlider.setObjectName(u"mouseSpeedSlider")
        self.mouseSpeedSlider.setOrientation(Qt.Horizontal)
        self.mouseSpeedSlider.setMinimum(1)
        self.mouseSpeedSlider.setMaximum(20)
        self.mouseSpeedSlider.setValue(5)
        self.mouseSpeedSlider.setTickPosition(QSlider.TicksBelow)
        self.mouseSpeedSlider.setTickInterval(1)

        self.vboxLayout.addWidget(self.mouseSpeedSlider)

        self.speedValueLabel = QLabel(self.centralWidget)
        self.speedValueLabel.setObjectName(u"speedValueLabel")
        self.speedValueLabel.setStyleSheet(u"color: #505050; font-size: 9pt; min-width:\n"
"                                        30px;")

        self.vboxLayout.addWidget(self.speedValueLabel)


        self.verticalLayout.addLayout(self.vboxLayout)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setSpacing(10)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.toggleEnabledLabel = QLabel(self.centralWidget)
        self.toggleEnabledLabel.setObjectName(u"toggleEnabledLabel")

        self.hboxLayout.addWidget(self.toggleEnabledLabel)

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout.addItem(self.spacerItem)

        self.toggleEnabledKey = QLineEdit(self.centralWidget)
        self.toggleEnabledKey.setObjectName(u"toggleEnabledKey")

        self.hboxLayout.addWidget(self.toggleEnabledKey)


        self.verticalLayout.addLayout(self.hboxLayout)

        self.centerControlLayout = QHBoxLayout()
        self.centerControlLayout.setSpacing(10)
        self.centerControlLayout.setObjectName(u"centerControlLayout")
        self.centerControlLabel = QLabel(self.centralWidget)
        self.centerControlLabel.setObjectName(u"centerControlLabel")

        self.centerControlLayout.addWidget(self.centerControlLabel)

        self.spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.centerControlLayout.addItem(self.spacerItem1)

        self.centerControlKey = QLineEdit(self.centralWidget)
        self.centerControlKey.setObjectName(u"centerControlKey")

        self.centerControlLayout.addWidget(self.centerControlKey)


        self.verticalLayout.addLayout(self.centerControlLayout)

        self.enableFreelookLayout = QHBoxLayout()
        self.enableFreelookLayout.setSpacing(10)
        self.enableFreelookLayout.setObjectName(u"enableFreelookLayout")
        self.enableFreelookLabel = QLabel(self.centralWidget)
        self.enableFreelookLabel.setObjectName(u"enableFreelookLabel")

        self.enableFreelookLayout.addWidget(self.enableFreelookLabel)

        self.spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.enableFreelookLayout.addItem(self.spacerItem2)

        self.enableFreelookKey = QLineEdit(self.centralWidget)
        self.enableFreelookKey.setObjectName(u"enableFreelookKey")

        self.enableFreelookLayout.addWidget(self.enableFreelookKey)


        self.verticalLayout.addLayout(self.enableFreelookLayout)

        self.viewCenterLayout = QHBoxLayout()
        self.viewCenterLayout.setSpacing(10)
        self.viewCenterLayout.setObjectName(u"viewCenterLayout")
        self.viewCenterLabel = QLabel(self.centralWidget)
        self.viewCenterLabel.setObjectName(u"viewCenterLabel")

        self.viewCenterLayout.addWidget(self.viewCenterLabel)

        self.spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.viewCenterLayout.addItem(self.spacerItem3)

        self.viewCenterKey = QLineEdit(self.centralWidget)
        self.viewCenterKey.setObjectName(u"viewCenterKey")

        self.viewCenterLayout.addWidget(self.viewCenterKey)


        self.verticalLayout.addLayout(self.viewCenterLayout)

        self.cameraFovLayout = QHBoxLayout()
        self.cameraFovLayout.setSpacing(10)
        self.cameraFovLayout.setObjectName(u"cameraFovLayout")
        self.cameraFovLabel = QLabel(self.centralWidget)
        self.cameraFovLabel.setObjectName(u"cameraFovLabel")

        self.cameraFovLayout.addWidget(self.cameraFovLabel)

        self.spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.cameraFovLayout.addItem(self.spacerItem4)

        self.cameraFovSpinBox = QSpinBox(self.centralWidget)
        self.cameraFovSpinBox.setObjectName(u"cameraFovSpinBox")
        self.cameraFovSpinBox.setValue(0)
        self.cameraFovSpinBox.setMinimum(60)
        self.cameraFovSpinBox.setMaximum(120)

        self.cameraFovLayout.addWidget(self.cameraFovSpinBox)


        self.verticalLayout.addLayout(self.cameraFovLayout)

        self.taxiModeLayout = QHBoxLayout()
        self.taxiModeLayout.setSpacing(10)
        self.taxiModeLayout.setObjectName(u"taxiModeLayout")
        self.taxiModeLabel = QLabel(self.centralWidget)
        self.taxiModeLabel.setObjectName(u"taxiModeLabel")

        self.taxiModeLayout.addWidget(self.taxiModeLabel)

        self.spacerItem5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.taxiModeLayout.addItem(self.spacerItem5)

        self.taxiModeKey = QLineEdit(self.centralWidget)
        self.taxiModeKey.setObjectName(u"taxiModeKey")

        self.taxiModeLayout.addWidget(self.taxiModeKey)


        self.verticalLayout.addLayout(self.taxiModeLayout)

        self.controlModeDescription = QLabel(self.centralWidget)
        self.controlModeDescription.setObjectName(u"controlModeDescription")
        self.controlModeDescription.setStyleSheet(u"color: #505050; font-size: 9pt;")
        self.controlModeDescription.setWordWrap(True)

        self.verticalLayout.addWidget(self.controlModeDescription)

        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setSpacing(5)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.controllerLayout = QVBoxLayout()
        self.controllerLayout.setSpacing(5)
        self.controllerLayout.setObjectName(u"controllerLayout")
        self.controllerLabel = QLabel(self.centralWidget)
        self.controllerLabel.setObjectName(u"controllerLabel")

        self.controllerLayout.addWidget(self.controllerLabel)

        self.controllerComboBox = QComboBox(self.centralWidget)
        self.controllerComboBox.setObjectName(u"controllerComboBox")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.controllerComboBox.sizePolicy().hasHeightForWidth())
        self.controllerComboBox.setSizePolicy(sizePolicy)

        self.controllerLayout.addWidget(self.controllerComboBox)


        self.vboxLayout1.addLayout(self.controllerLayout)


        self.verticalLayout.addLayout(self.vboxLayout1)

        self.ControllerVerticalLayout = QVBoxLayout()
        self.ControllerVerticalLayout.setSpacing(8)
        self.ControllerVerticalLayout.setObjectName(u"ControllerVerticalLayout")

        self.verticalLayout.addLayout(self.ControllerVerticalLayout)

        self.spacerItem6 = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.spacerItem6)

        self.optionsTitleLabel = QLabel(self.centralWidget)
        self.optionsTitleLabel.setObjectName(u"optionsTitleLabel")
        self.optionsTitleLabel.setAlignment(Qt.AlignCenter)
        self.optionsTitleLabel.setStyleSheet(u"font-size: 14pt; font-weight: bold;\n"
"                                color: #000000;")

        self.verticalLayout.addWidget(self.optionsTitleLabel)

        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.setSpacing(8)
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setSpacing(10)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.showCursorLabel = QLabel(self.centralWidget)
        self.showCursorLabel.setObjectName(u"showCursorLabel")

        self.hboxLayout1.addWidget(self.showCursorLabel)

        self.spacerItem7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem7)

        self.showCursorOption = QCheckBox(self.centralWidget)
        self.showCursorOption.setObjectName(u"showCursorOption")
        self.showCursorOption.setChecked(False)

        self.hboxLayout1.addWidget(self.showCursorOption)


        self.vboxLayout2.addLayout(self.hboxLayout1)

        self.hboxLayout2 = QHBoxLayout()
        self.hboxLayout2.setSpacing(10)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.hintOverlayLabel = QLabel(self.centralWidget)
        self.hintOverlayLabel.setObjectName(u"hintOverlayLabel")

        self.hboxLayout2.addWidget(self.hintOverlayLabel)

        self.spacerItem8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout2.addItem(self.spacerItem8)

        self.hintOverlayOption = QCheckBox(self.centralWidget)
        self.hintOverlayOption.setObjectName(u"hintOverlayOption")
        self.hintOverlayOption.setChecked(False)

        self.hboxLayout2.addWidget(self.hintOverlayOption)


        self.vboxLayout2.addLayout(self.hboxLayout2)

        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setSpacing(10)
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.showIndicatorLabel = QLabel(self.centralWidget)
        self.showIndicatorLabel.setObjectName(u"showIndicatorLabel")

        self.hboxLayout3.addWidget(self.showIndicatorLabel)

        self.spacerItem9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout3.addItem(self.spacerItem9)

        self.showIndicatorOption = QCheckBox(self.centralWidget)
        self.showIndicatorOption.setObjectName(u"showIndicatorOption")
        self.showIndicatorOption.setChecked(False)

        self.hboxLayout3.addWidget(self.showIndicatorOption)


        self.vboxLayout2.addLayout(self.hboxLayout3)

        self.hboxLayout4 = QHBoxLayout()
        self.hboxLayout4.setSpacing(10)
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.buttonMappingLabel = QLabel(self.centralWidget)
        self.buttonMappingLabel.setObjectName(u"buttonMappingLabel")

        self.hboxLayout4.addWidget(self.buttonMappingLabel)

        self.spacerItem10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout4.addItem(self.spacerItem10)

        self.buttonMappingOption = QCheckBox(self.centralWidget)
        self.buttonMappingOption.setObjectName(u"buttonMappingOption")
        self.buttonMappingOption.setChecked(False)

        self.hboxLayout4.addWidget(self.buttonMappingOption)


        self.vboxLayout2.addLayout(self.hboxLayout4)

        self.hboxLayout5 = QHBoxLayout()
        self.hboxLayout5.setSpacing(10)
        self.hboxLayout5.setObjectName(u"hboxLayout5")
        self.memorizeAxisPosLabel = QLabel(self.centralWidget)
        self.memorizeAxisPosLabel.setObjectName(u"memorizeAxisPosLabel")

        self.hboxLayout5.addWidget(self.memorizeAxisPosLabel)

        self.spacerItem11 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout5.addItem(self.spacerItem11)

        self.memorizeAxisPosOption = QCheckBox(self.centralWidget)
        self.memorizeAxisPosOption.setObjectName(u"memorizeAxisPosOption")
        self.memorizeAxisPosOption.setChecked(False)

        self.hboxLayout5.addWidget(self.memorizeAxisPosOption)


        self.vboxLayout2.addLayout(self.hboxLayout5)

        self.hboxLayout6 = QHBoxLayout()
        self.hboxLayout6.setSpacing(10)
        self.hboxLayout6.setObjectName(u"hboxLayout6")
        self.freelookAutoCenterLabel = QLabel(self.centralWidget)
        self.freelookAutoCenterLabel.setObjectName(u"freelookAutoCenterLabel")

        self.hboxLayout6.addWidget(self.freelookAutoCenterLabel)

        self.spacerItem12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout6.addItem(self.spacerItem12)

        self.freelookAutoCenterOption = QCheckBox(self.centralWidget)
        self.freelookAutoCenterOption.setObjectName(u"freelookAutoCenterOption")
        self.freelookAutoCenterOption.setChecked(False)

        self.hboxLayout6.addWidget(self.freelookAutoCenterOption)


        self.vboxLayout2.addLayout(self.hboxLayout6)


        self.verticalLayout.addLayout(self.vboxLayout2)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.spacerItem13 = QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.spacerItem13)

        self.startBtn = QPushButton(self.centralWidget)
        self.startBtn.setObjectName(u"startBtn")

        self.verticalLayout.addWidget(self.startBtn)

        self.statusLabel = QLabel(self.centralWidget)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.statusLabel)

        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.controlsTitleLabel.setText("")
        self.speedLabel.setText("")
        self.speedValueLabel.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.toggleEnabledLabel.setText("")
        self.toggleEnabledKey.setText("")
        self.centerControlLabel.setText("")
        self.centerControlKey.setText("")
        self.enableFreelookLabel.setText("")
        self.enableFreelookKey.setText("")
        self.viewCenterLabel.setText("")
        self.viewCenterKey.setText("")
        self.cameraFovLabel.setText("")
        self.taxiModeLabel.setText("")
        self.taxiModeKey.setText("")
        self.controlModeDescription.setText("")
        self.controllerLabel.setText("")
        self.optionsTitleLabel.setText("")
        self.showCursorLabel.setText("")
        self.hintOverlayLabel.setText("")
        self.showIndicatorLabel.setText("")
        self.buttonMappingLabel.setText("")
        self.memorizeAxisPosLabel.setText("")
        self.freelookAutoCenterLabel.setText("")
        self.startBtn.setText("")
        self.statusLabel.setText("")
        pass
    # retranslateUi

