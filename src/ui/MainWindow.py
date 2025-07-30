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
"                min-width: 120px;\n"
"                max-width: 240px;\n"
"                }\n"
"                #controllerComboBox {\n"
"                border"
                        ": 1px solid #A0A0A0;\n"
"                border-radius: 3px;\n"
"                padding: 4px;\n"
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
"                selection-backgrou"
                        "nd-color: #E1E1E1;\n"
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

        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setSpacing(5)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.controllerLayout = QVBoxLayout()
        self.controllerLayout.setSpacing(15)
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

        self.controllerHint = QLabel(self.centralWidget)
        self.controllerHint.setObjectName(u"controllerHint")
        self.controllerHint.setStyleSheet(u"color: #505050; font-size: 9pt; min-width:\n"
"                                        30px;")

        self.vboxLayout1.addWidget(self.controllerHint)


        self.verticalLayout.addLayout(self.vboxLayout1)

        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setSpacing(10)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.viewCenterOnCtrlLabel = QLabel(self.centralWidget)
        self.viewCenterOnCtrlLabel.setObjectName(u"viewCenterOnCtrlLabel")

        self.hboxLayout1.addWidget(self.viewCenterOnCtrlLabel)

        self.spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem2)

        self.viewCenterOnCtrlOption = QCheckBox(self.centralWidget)
        self.viewCenterOnCtrlOption.setObjectName(u"viewCenterOnCtrlOption")
        self.viewCenterOnCtrlOption.setChecked(False)

        self.hboxLayout1.addWidget(self.viewCenterOnCtrlOption)


        self.verticalLayout.addLayout(self.hboxLayout1)

        self.hboxLayout2 = QHBoxLayout()
        self.hboxLayout2.setSpacing(10)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.zoomNormalOnCtrlLabel = QLabel(self.centralWidget)
        self.zoomNormalOnCtrlLabel.setObjectName(u"zoomNormalOnCtrlLabel")

        self.hboxLayout2.addWidget(self.zoomNormalOnCtrlLabel)

        self.spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout2.addItem(self.spacerItem3)

        self.zoomNormalOnCtrlOption = QCheckBox(self.centralWidget)
        self.zoomNormalOnCtrlOption.setObjectName(u"zoomNormalOnCtrlOption")
        self.zoomNormalOnCtrlOption.setChecked(False)

        self.hboxLayout2.addWidget(self.zoomNormalOnCtrlOption)


        self.verticalLayout.addLayout(self.hboxLayout2)

        self.optionsTitleLabel = QLabel(self.centralWidget)
        self.optionsTitleLabel.setObjectName(u"optionsTitleLabel")
        self.optionsTitleLabel.setAlignment(Qt.AlignCenter)
        self.optionsTitleLabel.setStyleSheet(u"font-size: 14pt; font-weight: bold;\n"
"                                color: #000000;")

        self.verticalLayout.addWidget(self.optionsTitleLabel)

        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.setSpacing(8)
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setSpacing(10)
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.showCursorLabel = QLabel(self.centralWidget)
        self.showCursorLabel.setObjectName(u"showCursorLabel")

        self.hboxLayout3.addWidget(self.showCursorLabel)

        self.spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout3.addItem(self.spacerItem4)

        self.showCursorOption = QCheckBox(self.centralWidget)
        self.showCursorOption.setObjectName(u"showCursorOption")
        self.showCursorOption.setChecked(False)

        self.hboxLayout3.addWidget(self.showCursorOption)


        self.vboxLayout2.addLayout(self.hboxLayout3)

        self.hboxLayout4 = QHBoxLayout()
        self.hboxLayout4.setSpacing(10)
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.hintOverlayLabel = QLabel(self.centralWidget)
        self.hintOverlayLabel.setObjectName(u"hintOverlayLabel")

        self.hboxLayout4.addWidget(self.hintOverlayLabel)

        self.spacerItem5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout4.addItem(self.spacerItem5)

        self.hintOverlayOption = QCheckBox(self.centralWidget)
        self.hintOverlayOption.setObjectName(u"hintOverlayOption")
        self.hintOverlayOption.setChecked(False)

        self.hboxLayout4.addWidget(self.hintOverlayOption)


        self.vboxLayout2.addLayout(self.hboxLayout4)

        self.hboxLayout5 = QHBoxLayout()
        self.hboxLayout5.setSpacing(10)
        self.hboxLayout5.setObjectName(u"hboxLayout5")
        self.buttonMappingLabel = QLabel(self.centralWidget)
        self.buttonMappingLabel.setObjectName(u"buttonMappingLabel")

        self.hboxLayout5.addWidget(self.buttonMappingLabel)

        self.spacerItem6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout5.addItem(self.spacerItem6)

        self.buttonMappingOption = QCheckBox(self.centralWidget)
        self.buttonMappingOption.setObjectName(u"buttonMappingOption")
        self.buttonMappingOption.setChecked(False)

        self.hboxLayout5.addWidget(self.buttonMappingOption)


        self.vboxLayout2.addLayout(self.hboxLayout5)

        self.hboxLayout6 = QHBoxLayout()
        self.hboxLayout6.setSpacing(10)
        self.hboxLayout6.setObjectName(u"hboxLayout6")
        self.memorizeAxisPosLabel = QLabel(self.centralWidget)
        self.memorizeAxisPosLabel.setObjectName(u"memorizeAxisPosLabel")

        self.hboxLayout6.addWidget(self.memorizeAxisPosLabel)

        self.spacerItem7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout6.addItem(self.spacerItem7)

        self.memorizeAxisPosOption = QCheckBox(self.centralWidget)
        self.memorizeAxisPosOption.setObjectName(u"memorizeAxisPosOption")
        self.memorizeAxisPosOption.setChecked(False)

        self.hboxLayout6.addWidget(self.memorizeAxisPosOption)


        self.vboxLayout2.addLayout(self.hboxLayout6)

        self.hboxLayout7 = QHBoxLayout()
        self.hboxLayout7.setSpacing(10)
        self.hboxLayout7.setObjectName(u"hboxLayout7")
        self.wheelAxisModeLabel = QLabel(self.centralWidget)
        self.wheelAxisModeLabel.setObjectName(u"wheelAxisModeLabel")

        self.hboxLayout7.addWidget(self.wheelAxisModeLabel)

        self.spacerItem8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout7.addItem(self.spacerItem8)

        self.wheelAxisModeOption = QCheckBox(self.centralWidget)
        self.wheelAxisModeOption.setObjectName(u"wheelAxisModeOption")
        self.wheelAxisModeOption.setChecked(False)

        self.hboxLayout7.addWidget(self.wheelAxisModeOption)


        self.vboxLayout2.addLayout(self.hboxLayout7)


        self.verticalLayout.addLayout(self.vboxLayout2)

        self.verticalSpacer_sensitivity = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_sensitivity)

        self.spacerItem9 = QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.spacerItem9)

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
        self.controllerLabel.setText("")
        self.controllerHint.setText(QCoreApplication.translate("MainWindow", u"\u4ee5\u4e0b\u7684\u9009\u9879\u4f9d\u8d56\u6b63\u786e\u7684\u63a7\u5236\u5668", None))
        self.viewCenterOnCtrlLabel.setText("")
        self.zoomNormalOnCtrlLabel.setText("")
        self.optionsTitleLabel.setText("")
        self.showCursorLabel.setText("")
        self.hintOverlayLabel.setText("")
        self.buttonMappingLabel.setText("")
        self.memorizeAxisPosLabel.setText("")
        self.wheelAxisModeLabel.setText("")
        self.startBtn.setText("")
        self.statusLabel.setText("")
        pass
    # retranslateUi

