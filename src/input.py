import win32api
import win32con
import ctypes

class InputStateMonitor:
    def __init__(self):
        # 初始化鼠标状态
        self.mouse_buttons = {
            "left": False,
            "right": False,
            "middle": False,
            "xbutton1": False,
            "xbutton2": False
        }

        # 初始化键盘状态
        self.key_states = {}

        # 鼠标位置
        self.mouse_x = 0
        self.mouse_y = 0

        # 鼠标滚轮状态
        self.wheel_delta = 0

        # 设置虚拟键码映射 - 使用实际数值替代常量
        self.VK_MAP = {
            win32con.VK_LBUTTON: "left",
            win32con.VK_RBUTTON: "right",
            win32con.VK_MBUTTON: "middle",
            0x05: "xbutton1",  # VK_XBUTTON1
            0x06: "xbutton2",  # VK_XBUTTON2
            win32con.VK_SHIFT: "shift",
            win32con.VK_CONTROL: "ctrl",
            win32con.VK_MENU: "alt",
            win32con.VK_SPACE: "space",
            win32con.VK_RETURN: "enter",
            win32con.VK_ESCAPE: "esc",
            win32con.VK_TAB: "tab",
            win32con.VK_CAPITAL: "capslock",
            win32con.VK_BACK: "backspace",
            win32con.VK_INSERT: "insert",
            win32con.VK_DELETE: "delete",
            win32con.VK_HOME: "home",
            win32con.VK_END: "end",
            win32con.VK_PRIOR: "pageup",
            win32con.VK_NEXT: "pagedown",
            win32con.VK_UP: "up",
            win32con.VK_DOWN: "down",
            win32con.VK_LEFT: "left",
            win32con.VK_RIGHT: "right",
            win32con.VK_F1: "f1",
            win32con.VK_F2: "f2",
            win32con.VK_F3: "f3",
            win32con.VK_F4: "f4",
            win32con.VK_F5: "f5",
            win32con.VK_F6: "f6",
            win32con.VK_F7: "f7",
            win32con.VK_F8: "f8",
            win32con.VK_F9: "f9",
            win32con.VK_F10: "f10",
            win32con.VK_F11: "f11",
            win32con.VK_F12: "f12"
        }

        # 添加字母和数字键
        for i in range(ord('A'), ord('Z') + 1):
            self.VK_MAP[i] = chr(i).lower()

        for i in range(ord('0'), ord('9') + 1):
            self.VK_MAP[i] = chr(i)

        # 添加特殊字符 - 使用实际数值
        # 这些是Windows虚拟键码的十六进制值
        special_chars = {
            0xBA: ';',  # VK_OEM_1
            0xBB: '=',  # VK_OEM_PLUS
            0xBC: ',',  # VK_OEM_COMMA
            0xBD: '-',  # VK_OEM_MINUS
            0xBE: '.',  # VK_OEM_PERIOD
            0xBF: '/',  # VK_OEM_2
            0xC0: '`',  # VK_OEM_3
            0xDB: '[',  # VK_OEM_4
            0xDC: '\\', # VK_OEM_5
            0xDD: ']',  # VK_OEM_6
            0xDE: "'"   # VK_OEM_7
        }
        self.VK_MAP.update(special_chars)

    def update(self):
        """更新所有输入状态"""
        self._update_mouse_state()
        self._update_keyboard_state()
        self._update_mouse_position()

    def _update_mouse_state(self):
        """更新鼠标按钮状态"""
        self.mouse_buttons["LB"] = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0
        self.mouse_buttons["RB"] = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0
        self.mouse_buttons["MB"] = win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0

    def _update_keyboard_state(self):
        """更新键盘按键状态"""
        # 只更新映射表中存在的键
        for vk_code, key_name in self.VK_MAP.items():
            state = win32api.GetAsyncKeyState(vk_code)
            # 高位为1表示当前按下，低位为1表示上次调用后按过
            self.key_states[key_name] = (state & 0x8000) != 0

    def _update_mouse_position(self):
        """更新鼠标位置"""
        try:
            self.mouse_x, self.mouse_y = win32api.GetCursorPos()
        except:
            # 处理可能的异常
            pass

    def is_mouse_pressed(self, button_name):
        """检查鼠标按钮是否按下"""
        if isinstance(button_name, str):
            return self.mouse_buttons.get(button_name.upper(), False)

    def is_key_pressed(self, key_name):
        """检查键盘按键是否按下"""
        # 处理字符串输入
        if isinstance(key_name, str):
            return self.key_states.get(key_name.lower(), False)

        # 处理虚拟键码
        if isinstance(key_name, int):
            key_name = self.VK_MAP.get(key_name, None)
            if key_name:
                return self.key_states.get(key_name, False)

        return False

    def is_pressed(self, name):
        return self.is_key_pressed(name) or self.is_mouse_pressed(name)

    def get_mouse_position(self):
        """获取当前鼠标位置"""
        return self.mouse_x, self.mouse_y

    def set_mouse_position(self, x, y):
        """设置鼠标位置"""
        try:
            win32api.SetCursorPos((int(x), int(y)))
            self.mouse_x, self.mouse_y = x, y
        except:
            pass

    def get_mouse_delta(self, prev_x, prev_y):
        """计算鼠标移动增量"""
        return self.mouse_x - prev_x, self.mouse_y - prev_y

    def reset_wheel(self):
        """重置滚轮状态"""
        self.wheel_delta = 0

    def get_wheel_delta(self):
        """获取滚轮增量（需外部设置）"""
        return self.wheel_delta

    def set_wheel_delta(self, delta):
        """设置滚轮增量（通常由外部事件触发）"""
        self.wheel_delta = delta