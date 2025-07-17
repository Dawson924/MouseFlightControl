# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
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
        MainWindow.resize(350, 250)
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"    background-color: #F0F0F0;\n"
"    font-family: 'Segoe UI';\n"
"    font-size: 9pt;\n"
"}\n"
"QWidget {\n"
"    background-color: #F0F0F0;\n"
"}\n"
"QLabel {\n"
"    color: #000000;\n"
"}\n"
"QPushButton {\n"
"    background-color: #E1E1E1;\n"
"    border: 1px solid #A0A0A0;\n"
"    border-radius: 3px;\n"
"    padding: 5px;\n"
"    min-width: 80px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #D0D0D0;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #C0C0C0;\n"
"    border: 1px solid #707070;\n"
"}\n"
"QSlider::groove:horizontal {\n"
"    border: 1px solid #A0A0A0;\n"
"    height: 6px;\n"
"    background: #D0D0D0;\n"
"    margin: 2px 0;\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background: #E1E1E1;\n"
"    border: 1px solid #707070;\n"
"    width: 16px;\n"
"    margin: -4px 0;\n"
"    border-radius: 3px;\n"
"}\n"
"QSlider::handle:horizontal:hover {\n"
"    background: #F0F0F0;\n"
"}\n"
"QSlider::add-page:horizontal {\n"
"    background: #B0B0B0;\n"
"}\n"
"QSlider:"
                        ":sub-page:horizontal {\n"
"    background: #0078D7;\n"
"}\n"
"QStatusBar {\n"
"    background-color: #E1E1E1;\n"
"    border-top: 1px solid #A0A0A0;\n"
"    padding: 2px;\n"
"}")
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.centralWidget.setStyleSheet(u"background-color: #F0F0F0;")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.titleLabel = QLabel(self.centralWidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setStyleSheet(u"font-size: 14pt; font-weight: bold; margin: 10px 0; color: #000000;")

        self.verticalLayout.addWidget(self.titleLabel)

        self.speedLabel = QLabel(self.centralWidget)
        self.speedLabel.setObjectName(u"speedLabel")
        self.speedLabel.setStyleSheet(u"color: #000000;")

        self.verticalLayout.addWidget(self.speedLabel)

        self.mouseSpeedSlider = QSlider(self.centralWidget)
        self.mouseSpeedSlider.setObjectName(u"mouseSpeedSlider")
        self.mouseSpeedSlider.setOrientation(Qt.Horizontal)
        self.mouseSpeedSlider.setMinimum(1)
        self.mouseSpeedSlider.setMaximum(10)
        self.mouseSpeedSlider.setValue(5)
        self.mouseSpeedSlider.setTickPosition(QSlider.TicksBelow)
        self.mouseSpeedSlider.setTickInterval(1)

        self.verticalLayout.addWidget(self.mouseSpeedSlider)

        self.speedValueLabel = QLabel(self.centralWidget)
        self.speedValueLabel.setObjectName(u"speedValueLabel")
        self.speedValueLabel.setStyleSheet(u"color: #505050; font-size: 9pt;")

        self.verticalLayout.addWidget(self.speedValueLabel)

        self.startBtn = QPushButton(self.centralWidget)
        self.startBtn.setObjectName(u"startBtn")
        self.startBtn.setStyleSheet(u"font-size: 10pt; \n"
"padding: 8px; \n"
"margin: 10px 0;\n"
"background-color: #E1E1E1;")

        self.verticalLayout.addWidget(self.startBtn)

        self.statusLabel = QLabel(self.centralWidget)
        self.statusLabel.setObjectName(u"statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setStyleSheet(u"color: #505050; font-style: italic;")

        self.verticalLayout.addWidget(self.statusLabel)

        MainWindow.setCentralWidget(self.centralWidget)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        self.statusBar.setStyleSheet(u"background-color: #E1E1E1; border-top: 1px solid #A0A0A0;")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Mouse Control For DCS", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.speedLabel.setText(QCoreApplication.translate("MainWindow", u"\u7cfb\u7edf\u9f20\u6807\u7075\u654f\u5ea6:", None))
        self.speedValueLabel.setText(QCoreApplication.translate("MainWindow", u"\u5f53\u524d\u503c: Nan", None))
        self.startBtn.setText(QCoreApplication.translate("MainWindow", u"\u542f\u52a8", None))
        self.statusLabel.setText(QCoreApplication.translate("MainWindow", u"\u72b6\u6001: \u672a\u8fd0\u884c", None))
    # retranslateUi

