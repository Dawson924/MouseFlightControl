import socket
from controller.base import BaseController

class DCSController(BaseController):
    id = 'dcs_world'

    def __init__(self, vjoy):
        super().__init__(vjoy)
        self.ip = '127.0.0.1'
        self.port = 7779
        self.dcs_address = (self.ip, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"✅ 已连接到DCS: {self.ip}:{self.port}")

    def send(self, command, *params):
        # 构建完整命令字符串
        param_str = ",".join(str(p) for p in params)
        full_command = f"{command} {param_str}\n"

        # 发送命令
        self.sock.sendto(full_command.encode('utf-8'), self.dcs_address)
        print(f"📤 发送命令: {full_command.strip()}")

    def close(self):
        """关闭连接"""
        self.sock.close()
        print("🔌 连接已关闭")

    def __del__(self):
        self.close()

    def view_center(self):
        self.send("LoSetCommand", 36)
