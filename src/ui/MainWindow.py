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
"                font-family: 'Segoe UI';\n"
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
"                height: 6p"
                        "x;\n"
"                background: #D0D0D0;\n"
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
"                min-width: 80px;\n"
"                }\n"
"            ")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 0, 15, 15)
        self.titleLabel = QLabel(self.centralWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet(u"font-size: 14pt; font-weight: bold; margin: 10px 0;\n"
"                                color: #000000;")

        self.verticalLayout.addWidget(self.titleLabel)

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
        self.mouseSpeedSlider.setMaximum(10)
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

        self.fixedVerticalSpacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.fixedVerticalSpacer)

        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setSpacing(8)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setSpacing(10)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.cursorOverhaulLabel = QLabel(self.centralWidget)
        self.cursorOverhaulLabel.setObjectName(u"cursorOverhaulLabel")

        self.hboxLayout.addWidget(self.cursorOverhaulLabel)

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout.addItem(self.spacerItem)

        self.cursorOverhaulOption = QCheckBox(self.centralWidget)
        self.cursorOverhaulOption.setObjectName(u"cursorOverhaulOption")
        self.cursorOverhaulOption.setChecked(False)

        self.hboxLayout.addWidget(self.cursorOverhaulOption)


        self.vboxLayout1.addLayout(self.hboxLayout)

        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setSpacing(10)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.interfaceOverlayLabel = QLabel(self.centralWidget)
        self.interfaceOverlayLabel.setObjectName(u"interfaceOverlayLabel")

        self.hboxLayout1.addWidget(self.interfaceOverlayLabel)

        self.spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem1)

        self.interfaceOverlayOption = QCheckBox(self.centralWidget)
        self.interfaceOverlayOption.setObjectName(u"interfaceOverlayOption")
        self.interfaceOverlayOption.setChecked(False)

        self.hboxLayout1.addWidget(self.interfaceOverlayOption)


        self.vboxLayout1.addLayout(self.hboxLayout1)

        self.hboxLayout2 = QHBoxLayout()
        self.hboxLayout2.setSpacing(10)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.toggleEnabledLabel = QLabel(self.centralWidget)
        self.toggleEnabledLabel.setObjectName(u"toggleEnabledLabel")

        self.hboxLayout2.addWidget(self.toggleEnabledLabel)

        self.spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout2.addItem(self.spacerItem2)

        self.toggleEnabledKey = QLineEdit(self.centralWidget)
        self.toggleEnabledKey.setObjectName(u"toggleEnabledKey")

        self.hboxLayout2.addWidget(self.toggleEnabledKey)


        self.vboxLayout1.addLayout(self.hboxLayout2)

        self.centerControlLayout = QHBoxLayout()
        self.centerControlLayout.setSpacing(10)
        self.centerControlLayout.setObjectName(u"centerControlLayout")
        self.centerControlLabel = QLabel(self.centralWidget)
        self.centerControlLabel.setObjectName(u"centerControlLabel")

        self.centerControlLayout.addWidget(self.centerControlLabel)

        self.spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.centerControlLayout.addItem(self.spacerItem3)

        self.centerControlKey = QLineEdit(self.centralWidget)
        self.centerControlKey.setObjectName(u"centerControlKey")

        self.centerControlLayout.addWidget(self.centerControlKey)


        self.vboxLayout1.addLayout(self.centerControlLayout)


        self.verticalLayout.addLayout(self.vboxLayout1)

        self.verticalSpacer_sensitivity = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_sensitivity)

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
        self.titleLabel.setText("")
        self.speedLabel.setText("")
        self.speedValueLabel.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.cursorOverhaulLabel.setText("")
        self.interfaceOverlayLabel.setText("")
        self.toggleEnabledLabel.setText("")
        self.toggleEnabledKey.setText("")
        self.centerControlLabel.setText("")
        self.centerControlKey.setText("")
        self.startBtn.setText("")
        self.statusLabel.setText("")
        pass
    # retranslateUi

