import socket
from controller.base import BaseController

class DCSController(BaseController):
    def __init__(self, vjoy):
        super().__init__(vjoy)
        self.ip = '127.0.0.1'
        self.port = 7779
        self.dcs_address = (self.ip, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)  # 设置1秒超时

        # 验证连接状态
        self.connected = self._validate_connection()
        if self.connected:
            print(f"✅ 已连接到DCS: {self.ip}:{self.port}")
        else:
            print(f"⚠️ 无法连接到DCS: {self.ip}:{self.port} - 请确保DCS正在运行且导出设置正确")

    def _validate_connection(self):
        """尝试发送测试命令验证连接"""
        try:
            self.sock.sendto(b"HELLO\n", self.dcs_address)
            self.sock.recvfrom(1024)
        except socket.timeout:
            return True
        except socket.error as e:
            if e.errno == 10054:
                return False
            print(f"⚠️ 连接错误: {e}")
            return False
        return True

    def send(self, command, *params):
        """发送命令到DCS"""
        param_str = ",".join(str(p) for p in params)
        full_command = f"{command} {param_str}\n"

        try:
            self.sock.sendto(full_command.encode('utf-8'), self.dcs_address)
            print(f"📤 发送命令: {full_command.strip()}")
            return True
        except socket.error as e:
            print(f"❌ 发送失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        self.sock.close()
        print("🔌 连接已关闭")

    def __del__(self):
        self.close()

    def view_center(self):
        self.send("LoSetCommand", 36)

    def zoom_normal(self):
        self.send("LoSetCommand", 177)

    def update(self, state, context):
        if state.input.alt_ctrl_shift() and state.input.is_pressed(context.key_toggle):
            if state.enabled and state.options.view_center_on_ctrl:
                self.view_center()
            if state.enabled and state.options.zoom_normal_on_ctrl:
                self.zoom_normal()
