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
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralLayout = QVBoxLayout(self.centralWidget)
        self.centralLayout.setSpacing(10)
        self.centralLayout.setObjectName(u"centralLayout")
        self.centralLayout.setContentsMargins(15, 10, 15, 15)
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.controlsTab = QWidget()
        self.controlsTab.setObjectName(u"controlsTab")
        self.verticalLayout = QVBoxLayout(self.controlsTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setSpacing(5)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.speedLabel = QLabel(self.controlsTab)
        self.speedLabel.setObjectName(u"speedLabel")
        self.speedLabel.setStyleSheet(u"color: #000000;")

        self.vboxLayout.addWidget(self.speedLabel)

        self.mouseSpeed = QSlider(self.controlsTab)
        self.mouseSpeed.setObjectName(u"mouseSpeed")
        self.mouseSpeed.setOrientation(Qt.Horizontal)
        self.mouseSpeed.setMinimum(1)
        self.mouseSpeed.setMaximum(20)
        self.mouseSpeed.setValue(5)
        self.mouseSpeed.setTickPosition(QSlider.TicksBelow)
        self.mouseSpeed.setTickInterval(1)

        self.vboxLayout.addWidget(self.mouseSpeed)

        self.speedValueLabel = QLabel(self.controlsTab)
        self.speedValueLabel.setObjectName(u"speedValueLabel")
        self.speedValueLabel.setStyleSheet(u"color: #505050; font-size:\n"
"                                                        9pt; min-width:\n"
"                                                        30px;")

        self.vboxLayout.addWidget(self.speedValueLabel)


        self.verticalLayout.addLayout(self.vboxLayout)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setSpacing(10)
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.toggleEnabledLabel = QLabel(self.controlsTab)
        self.toggleEnabledLabel.setObjectName(u"toggleEnabledLabel")

        self.hboxLayout.addWidget(self.toggleEnabledLabel)

        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout.addItem(self.spacerItem)

        self.toggleEnabledKey = QLineEdit(self.controlsTab)
        self.toggleEnabledKey.setObjectName(u"toggleEnabledKey")

        self.hboxLayout.addWidget(self.toggleEnabledKey)


        self.verticalLayout.addLayout(self.hboxLayout)

        self.centerControlLayout = QHBoxLayout()
        self.centerControlLayout.setSpacing(10)
        self.centerControlLayout.setObjectName(u"centerControlLayout")
        self.centerControlLabel = QLabel(self.controlsTab)
        self.centerControlLabel.setObjectName(u"centerControlLabel")

        self.centerControlLayout.addWidget(self.centerControlLabel)

        self.spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.centerControlLayout.addItem(self.spacerItem1)

        self.centerControlKey = QLineEdit(self.controlsTab)
        self.centerControlKey.setObjectName(u"centerControlKey")

        self.centerControlLayout.addWidget(self.centerControlKey)


        self.verticalLayout.addLayout(self.centerControlLayout)

        self.enableFreecamLayout = QHBoxLayout()
        self.enableFreecamLayout.setSpacing(10)
        self.enableFreecamLayout.setObjectName(u"enableFreecamLayout")
        self.enableFreecamLabel = QLabel(self.controlsTab)
        self.enableFreecamLabel.setObjectName(u"enableFreecamLabel")

        self.enableFreecamLayout.addWidget(self.enableFreecamLabel)

        self.spacerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.enableFreecamLayout.addItem(self.spacerItem2)

        self.enableFreecamKey = QLineEdit(self.controlsTab)
        self.enableFreecamKey.setObjectName(u"enableFreecamKey")

        self.enableFreecamLayout.addWidget(self.enableFreecamKey)


        self.verticalLayout.addLayout(self.enableFreecamLayout)

        self.viewCenterLayout = QHBoxLayout()
        self.viewCenterLayout.setSpacing(10)
        self.viewCenterLayout.setObjectName(u"viewCenterLayout")
        self.viewCenterLabel = QLabel(self.controlsTab)
        self.viewCenterLabel.setObjectName(u"viewCenterLabel")

        self.viewCenterLayout.addWidget(self.viewCenterLabel)

        self.spacerItem3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.viewCenterLayout.addItem(self.spacerItem3)

        self.viewCenterKey = QLineEdit(self.controlsTab)
        self.viewCenterKey.setObjectName(u"viewCenterKey")

        self.viewCenterLayout.addWidget(self.viewCenterKey)


        self.verticalLayout.addLayout(self.viewCenterLayout)

        self.cameraFovLayout = QHBoxLayout()
        self.cameraFovLayout.setSpacing(10)
        self.cameraFovLayout.setObjectName(u"cameraFovLayout")
        self.cameraFovLabel = QLabel(self.controlsTab)
        self.cameraFovLabel.setObjectName(u"cameraFovLabel")

        self.cameraFovLayout.addWidget(self.cameraFovLabel)

        self.spacerItem4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.cameraFovLayout.addItem(self.spacerItem4)

        self.cameraFovSpinBox = QSpinBox(self.controlsTab)
        self.cameraFovSpinBox.setObjectName(u"cameraFovSpinBox")
        self.cameraFovSpinBox.setValue(0)
        self.cameraFovSpinBox.setMinimum(40)
        self.cameraFovSpinBox.setMaximum(160)

        self.cameraFovLayout.addWidget(self.cameraFovSpinBox)


        self.verticalLayout.addLayout(self.cameraFovLayout)

        self.taxiModeLayout = QHBoxLayout()
        self.taxiModeLayout.setSpacing(10)
        self.taxiModeLayout.setObjectName(u"taxiModeLayout")
        self.taxiModeLabel = QLabel(self.controlsTab)
        self.taxiModeLabel.setObjectName(u"taxiModeLabel")

        self.taxiModeLayout.addWidget(self.taxiModeLabel)

        self.spacerItem5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.taxiModeLayout.addItem(self.spacerItem5)

        self.taxiModeKey = QLineEdit(self.controlsTab)
        self.taxiModeKey.setObjectName(u"taxiModeKey")

        self.taxiModeLayout.addWidget(self.taxiModeKey)


        self.verticalLayout.addLayout(self.taxiModeLayout)

        self.verticalSpacer = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.controlsTab, "")
        self.optionsTab = QWidget()
        self.optionsTab.setObjectName(u"optionsTab")
        self.verticalLayout2 = QVBoxLayout(self.optionsTab)
        self.verticalLayout2.setObjectName(u"verticalLayout2")
        self.vboxLayout1 = QVBoxLayout()
        self.vboxLayout1.setSpacing(8)
        self.vboxLayout1.setObjectName(u"vboxLayout1")
        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setSpacing(10)
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.showCursorLabel = QLabel(self.optionsTab)
        self.showCursorLabel.setObjectName(u"showCursorLabel")

        self.hboxLayout1.addWidget(self.showCursorLabel)

        self.spacerItem6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout1.addItem(self.spacerItem6)

        self.showCursorOption = QCheckBox(self.optionsTab)
        self.showCursorOption.setObjectName(u"showCursorOption")
        self.showCursorOption.setChecked(False)

        self.hboxLayout1.addWidget(self.showCursorOption)


        self.vboxLayout1.addLayout(self.hboxLayout1)

        self.hboxLayout2 = QHBoxLayout()
        self.hboxLayout2.setSpacing(10)
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.showHintLabel = QLabel(self.optionsTab)
        self.showHintLabel.setObjectName(u"showHintLabel")

        self.hboxLayout2.addWidget(self.showHintLabel)

        self.spacerItem7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout2.addItem(self.spacerItem7)

        self.showHintOption = QCheckBox(self.optionsTab)
        self.showHintOption.setObjectName(u"showHintOption")
        self.showHintOption.setChecked(False)

        self.hboxLayout2.addWidget(self.showHintOption)


        self.vboxLayout1.addLayout(self.hboxLayout2)

        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setSpacing(10)
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.showIndicatorLabel = QLabel(self.optionsTab)
        self.showIndicatorLabel.setObjectName(u"showIndicatorLabel")

        self.hboxLayout3.addWidget(self.showIndicatorLabel)

        self.spacerItem8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout3.addItem(self.spacerItem8)

        self.showIndicatorOption = QCheckBox(self.optionsTab)
        self.showIndicatorOption.setObjectName(u"showIndicatorOption")
        self.showIndicatorOption.setChecked(False)

        self.hboxLayout3.addWidget(self.showIndicatorOption)


        self.vboxLayout1.addLayout(self.hboxLayout3)

        self.hboxLayout4 = QHBoxLayout()
        self.hboxLayout4.setSpacing(10)
        self.hboxLayout4.setObjectName(u"hboxLayout4")
        self.buttonMappingLabel = QLabel(self.optionsTab)
        self.buttonMappingLabel.setObjectName(u"buttonMappingLabel")

        self.hboxLayout4.addWidget(self.buttonMappingLabel)

        self.spacerItem9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout4.addItem(self.spacerItem9)

        self.buttonMappingOption = QCheckBox(self.optionsTab)
        self.buttonMappingOption.setObjectName(u"buttonMappingOption")
        self.buttonMappingOption.setChecked(False)

        self.hboxLayout4.addWidget(self.buttonMappingOption)


        self.vboxLayout1.addLayout(self.hboxLayout4)

        self.hboxLayout5 = QHBoxLayout()
        self.hboxLayout5.setSpacing(10)
        self.hboxLayout5.setObjectName(u"hboxLayout5")
        self.memorizeAxisPosLabel = QLabel(self.optionsTab)
        self.memorizeAxisPosLabel.setObjectName(u"memorizeAxisPosLabel")

        self.hboxLayout5.addWidget(self.memorizeAxisPosLabel)

        self.spacerItem10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout5.addItem(self.spacerItem10)

        self.memorizeAxisPosOption = QCheckBox(self.optionsTab)
        self.memorizeAxisPosOption.setObjectName(u"memorizeAxisPosOption")
        self.memorizeAxisPosOption.setChecked(False)

        self.hboxLayout5.addWidget(self.memorizeAxisPosOption)


        self.vboxLayout1.addLayout(self.hboxLayout5)

        self.hboxLayout6 = QHBoxLayout()
        self.hboxLayout6.setSpacing(10)
        self.hboxLayout6.setObjectName(u"hboxLayout6")
        self.freecamAutoCenterLabel = QLabel(self.optionsTab)
        self.freecamAutoCenterLabel.setObjectName(u"freecamAutoCenterLabel")

        self.hboxLayout6.addWidget(self.freecamAutoCenterLabel)

        self.spacerItem11 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout6.addItem(self.spacerItem11)

        self.freecamAutoCenterOption = QCheckBox(self.optionsTab)
        self.freecamAutoCenterOption.setObjectName(u"freecamAutoCenterOption")
        self.freecamAutoCenterOption.setChecked(False)

        self.hboxLayout6.addWidget(self.freecamAutoCenterOption)


        self.vboxLayout1.addLayout(self.hboxLayout6)

        self.verticalSpacer2 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.vboxLayout1.addItem(self.verticalSpacer2)


        self.verticalLayout2.addLayout(self.vboxLayout1)

        self.tabWidget.addTab(self.optionsTab, "")
        self.axisTab = QWidget()
        self.axisTab.setObjectName(u"axisTab")
        self.verticalLayout3 = QVBoxLayout(self.axisTab)
        self.verticalLayout3.setObjectName(u"verticalLayout3")
        self.hboxLayout7 = QHBoxLayout()
        self.hboxLayout7.setSpacing(10)
        self.hboxLayout7.setObjectName(u"hboxLayout7")
        self.label = QLabel(self.axisTab)
        self.label.setObjectName(u"label")

        self.hboxLayout7.addWidget(self.label)

        self.spacerItem12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout7.addItem(self.spacerItem12)

        self.xAxisButton = QPushButton(self.axisTab)
        self.xAxisButton.setObjectName(u"xAxisButton")

        self.hboxLayout7.addWidget(self.xAxisButton)


        self.verticalLayout3.addLayout(self.hboxLayout7)

        self.hboxLayout8 = QHBoxLayout()
        self.hboxLayout8.setSpacing(10)
        self.hboxLayout8.setObjectName(u"hboxLayout8")
        self.label1 = QLabel(self.axisTab)
        self.label1.setObjectName(u"label1")

        self.hboxLayout8.addWidget(self.label1)

        self.spacerItem13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout8.addItem(self.spacerItem13)

        self.yAxisButton = QPushButton(self.axisTab)
        self.yAxisButton.setObjectName(u"yAxisButton")

        self.hboxLayout8.addWidget(self.yAxisButton)


        self.verticalLayout3.addLayout(self.hboxLayout8)

        self.hboxLayout9 = QHBoxLayout()
        self.hboxLayout9.setSpacing(10)
        self.hboxLayout9.setObjectName(u"hboxLayout9")
        self.label2 = QLabel(self.axisTab)
        self.label2.setObjectName(u"label2")

        self.hboxLayout9.addWidget(self.label2)

        self.spacerItem14 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout9.addItem(self.spacerItem14)

        self.zAxisButton = QPushButton(self.axisTab)
        self.zAxisButton.setObjectName(u"zAxisButton")

        self.hboxLayout9.addWidget(self.zAxisButton)


        self.verticalLayout3.addLayout(self.hboxLayout9)

        self.hboxLayout10 = QHBoxLayout()
        self.hboxLayout10.setSpacing(10)
        self.hboxLayout10.setObjectName(u"hboxLayout10")
        self.label3 = QLabel(self.axisTab)
        self.label3.setObjectName(u"label3")

        self.hboxLayout10.addWidget(self.label3)

        self.spacerItem15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout10.addItem(self.spacerItem15)

        self.rxAxisButton = QPushButton(self.axisTab)
        self.rxAxisButton.setObjectName(u"rxAxisButton")

        self.hboxLayout10.addWidget(self.rxAxisButton)


        self.verticalLayout3.addLayout(self.hboxLayout10)

        self.hboxLayout11 = QHBoxLayout()
        self.hboxLayout11.setSpacing(10)
        self.hboxLayout11.setObjectName(u"hboxLayout11")
        self.label4 = QLabel(self.axisTab)
        self.label4.setObjectName(u"label4")

        self.hboxLayout11.addWidget(self.label4)

        self.spacerItem16 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout11.addItem(self.spacerItem16)

        self.ryAxisButton = QPushButton(self.axisTab)
        self.ryAxisButton.setObjectName(u"ryAxisButton")

        self.hboxLayout11.addWidget(self.ryAxisButton)


        self.verticalLayout3.addLayout(self.hboxLayout11)

        self.hboxLayout12 = QHBoxLayout()
        self.hboxLayout12.setSpacing(10)
        self.hboxLayout12.setObjectName(u"hboxLayout12")
        self.label5 = QLabel(self.axisTab)
        self.label5.setObjectName(u"label5")

        self.hboxLayout12.addWidget(self.label5)

        self.spacerItem17 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.hboxLayout12.addItem(self.spacerItem17)

        self.rzAxisButton = QPushButton(self.axisTab)
        self.rzAxisButton.setObjectName(u"rzAxisButton")

        self.hboxLayout12.addWidget(self.rzAxisButton)


        self.verticalLayout3.addLayout(self.hboxLayout12)

        self.verticalSpacer3 = QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout3.addItem(self.verticalSpacer3)

        self.tabWidget.addTab(self.axisTab, "")

        self.centralLayout.addWidget(self.tabWidget)

        self.vboxLayout2 = QVBoxLayout()
        self.vboxLayout2.setSpacing(5)
        self.vboxLayout2.setObjectName(u"vboxLayout2")
        self.controllerLayout = QVBoxLayout()
        self.controllerLayout.setSpacing(5)
        self.controllerLayout.setObjectName(u"controllerLayout")
        self.controllerLabel = QLabel(self.centralWidget)
        self.controllerLabel.setObjectName(u"controllerLabel")

        self.controllerLayout.addWidget(self.controllerLabel)

        self.flightMode = QComboBox(self.centralWidget)
        self.flightMode.setObjectName(u"flightMode")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.flightMode.sizePolicy().hasHeightForWidth())
        self.flightMode.setSizePolicy(sizePolicy)

        self.controllerLayout.addWidget(self.flightMode)


        self.vboxLayout2.addLayout(self.controllerLayout)


        self.centralLayout.addLayout(self.vboxLayout2)

        self.ControllerVerticalLayout = QVBoxLayout()
        self.ControllerVerticalLayout.setSpacing(8)
        self.ControllerVerticalLayout.setObjectName(u"ControllerVerticalLayout")

        self.centralLayout.addLayout(self.ControllerVerticalLayout)

        self.startButton = QPushButton(self.centralWidget)
        self.startButton.setObjectName(u"startButton")

        self.centralLayout.addWidget(self.startButton)

        self.statusLabel = QLabel(self.centralWidget)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)

        self.centralLayout.addWidget(self.statusLabel)

        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.speedLabel.setText("")
        self.speedValueLabel.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.toggleEnabledLabel.setText("")
        self.toggleEnabledKey.setText("")
        self.centerControlLabel.setText("")
        self.centerControlKey.setText("")
        self.enableFreecamLabel.setText("")
        self.enableFreecamKey.setText("")
        self.viewCenterLabel.setText("")
        self.viewCenterKey.setText("")
        self.cameraFovLabel.setText("")
        self.taxiModeLabel.setText("")
        self.taxiModeKey.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.controlsTab), QCoreApplication.translate("MainWindow", u"CONTROLS", None))
        self.showCursorLabel.setText("")
        self.showHintLabel.setText("")
        self.showIndicatorLabel.setText("")
        self.buttonMappingLabel.setText("")
        self.memorizeAxisPosLabel.setText("")
        self.freecamAutoCenterLabel.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.optionsTab), QCoreApplication.translate("MainWindow", u"OPTIONS", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.xAxisButton.setText(QCoreApplication.translate("MainWindow", u"Modify", None))
        self.label1.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.yAxisButton.setText(QCoreApplication.translate("MainWindow", u"Modify", None))
        self.label2.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.zAxisButton.setText(QCoreApplication.translate("MainWindow", u"Modify", None))
        self.label3.setText(QCoreApplication.translate("MainWindow", u"RX", None))
        self.rxAxisButton.setText(QCoreApplication.translate("MainWindow", u"Modify", None))
        self.label4.setText(QCoreApplication.translate("MainWindow", u"RY", None))
        self.ryAxisButton.setText(QCoreApplication.translate("MainWindow", u"Modify", None))
        self.label5.setText(QCoreApplication.translate("MainWindow", u"RZ", None))
        self.rzAxisButton.setText(QCoreApplication.translate("MainWindow", u"Modify", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.axisTab), QCoreApplication.translate("MainWindow", u"AXIS", None))
        self.controllerLabel.setText("")
        self.startButton.setText("")
        self.statusLabel.setText("")
        pass
    # retranslateUi

