from PySide2.QtWidgets import QApplication, QLabel
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QFont

class HintLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_style = """
            background-color: rgba(0, 0, 0, 150);
            padding: 12px 24px;
            border-radius: 8px;
        """
        font = QFont()
        font.setPointSize(16)
        self.setFont(font)
        self.setStyleSheet(self.base_style)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint |
            Qt.Tool |                  # 工具窗口（不在任务栏显示）
            Qt.WindowDoesNotAcceptFocus |  # 不接受焦点（避免任务栏激活）
            Qt.WindowTransparentForInput  # 鼠标穿透（不拦截输入事件）
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

    def show_message(self, text, color='white', duration=3000):
        dynamic_style = f"color: {color};" + self.base_style
        self.setStyleSheet(dynamic_style)
        self.setText(text)
        self.adjustSize()

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = 50
        self.move(x, y)
        self.show()

        if duration > 0:
            QTimer.singleShot(duration, self.hide)
