from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtGui import QPixmap, QPainter, QCursor, QBitmap
from PySide2.QtCore import Qt, QTimer

class CursorGraph(QWidget):
    def __init__(self, cursor_path, size=(32, 32), parent=None):
        super().__init__(parent)
        # 初始隐藏
        self.is_visible = False

        # 窗口属性：无边框、透明、置顶、鼠标穿透
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint |
            Qt.Tool |                  # 工具窗口（不在任务栏显示）
            Qt.WindowDoesNotAcceptFocus |  # 不接受焦点（避免任务栏激活）
            Qt.WindowTransparentForInput  # 鼠标穿透（不拦截输入事件）
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 加载并缩放光标图标（支持高DPI）
        self.pixmap = QPixmap(cursor_path).scaled(
            size[0] * self.devicePixelRatio(),
            size[1] * self.devicePixelRatio(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.pixmap.setDevicePixelRatio(self.devicePixelRatio())
        self.resize(
            self.pixmap.width() // self.devicePixelRatio(),
            self.pixmap.height() // self.devicePixelRatio()
        )

        # 定时器：用于跟踪鼠标位置（初始不启动）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.setInterval(16)  # ~60Hz更新频率

        # 创建空白光标（用于隐藏系统原光标）
        self.blank_cursor = QCursor(QBitmap(1, 1), QBitmap(1, 1))  # 1x1透明光标

        # 初始隐藏窗口
        self.hide()

    def update_position(self):
        """跟随鼠标移动窗口"""
        if not self.is_visible:
            return
        global_pos = QCursor.pos()
        # 计算窗口位置（使图标中心对准鼠标位置）
        x = global_pos.x() - self.width() // 2
        y = global_pos.y() - self.height() // 2
        self.move(x, y)

    def paintEvent(self, event):
        """绘制自定义光标图标"""
        if not self.is_visible or self.pixmap.isNull():
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def show_cursor(self, flag):
        if flag:
            self.is_visible = True
            self.show()
            self.timer.start()  # 启动位置跟踪
            QApplication.setOverrideCursor(self.blank_cursor)
        else:
            self.is_visible = False
            self.timer.stop()  # 停止位置跟踪
            self.hide()
            QApplication.restoreOverrideCursor()
