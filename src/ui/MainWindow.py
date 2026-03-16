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
        self.connectTab = QWidget()
        self.connectTab.setObjectName(u"connectTab")
        self.connectPageLayout = QVBoxLayout(self.connectTab)
        self.connectPageLayout.setObjectName(u"connectPageLayout")
        self.tabWidget.addTab(self.connectTab, "")
        self.controlsTab = QWidget()
        self.controlsTab.setObjectName(u"controlsTab")
        self.controlsPageLayout = QVBoxLayout(self.controlsTab)
        self.controlsPageLayout.setObjectName(u"controlsPageLayout")
        self.tabWidget.addTab(self.controlsTab, "")
        self.optionsTab = QWidget()
        self.optionsTab.setObjectName(u"optionsTab")
        self.optionsPageLayout = QVBoxLayout(self.optionsTab)
        self.optionsPageLayout.setObjectName(u"optionsPageLayout")
        self.tabWidget.addTab(self.optionsTab, "")
        self.axisTab = QWidget()
        self.axisTab.setObjectName(u"axisTab")
        self.axisTunePageLayout = QVBoxLayout(self.axisTab)
        self.axisTunePageLayout.setObjectName(u"axisTunePageLayout")
        self.tabWidget.addTab(self.axisTab, "")

        self.centralLayout.addWidget(self.tabWidget)

        self.vboxLayout = QVBoxLayout()
        self.vboxLayout.setSpacing(5)
        self.vboxLayout.setObjectName(u"vboxLayout")
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


        self.vboxLayout.addLayout(self.controllerLayout)


        self.centralLayout.addLayout(self.vboxLayout)

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
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.connectTab), QCoreApplication.translate("MainWindow", u"CONNECT", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.controlsTab), QCoreApplication.translate("MainWindow", u"CONTROLS", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.optionsTab), QCoreApplication.translate("MainWindow", u"OPTIONS", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.axisTab), QCoreApplication.translate("MainWindow", u"AXIS", None))
        self.controllerLabel.setText("")
        self.startButton.setText("")
        self.statusLabel.setText("")
        pass
    # retranslateUi

