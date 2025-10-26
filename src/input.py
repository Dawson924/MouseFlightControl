import pydirectinput
from pynput import mouse
import win32api
import win32con
import threading

from utils import pos

class InputStateMonitor:
    def __init__(self, pause=0.016, retry=2):
        self.pause = pause
        self.retry = retry

        pydirectinput.PAUSE = self.pause
        pydirectinput.FAILSAFE = False

        # 初始化鼠标状态
        self.mouse_buttons = {
            "LMB": False,  # 左键
            "RMB": False,  # 右键
            "MMB": False,  # 中键
            "XMB1": False, # 侧键1
            "XMB2": False  # 侧键2
        }
        self.prev_mouse_buttons = self.mouse_buttons.copy()

        # 初始化键盘状态
        self.key_states = {}
        self.prev_key_states = {}

        # 鼠标位置
        self.mouse_x = 0
        self.mouse_y = 0

        # 鼠标滚轮状态
        self.wheel_delta = 0
        self.wheel_lock = threading.Lock()

        # 滚轮监听器
        self.mouse_listener = None

        # 设置虚拟键码映射
        self.VK_MAP = {
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
            win32con.VK_LWIN: "win",
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
            win32con.VK_F12: "f12",
        }

        # 添加字母和数字键
        for i in range(ord('A'), ord('Z') + 1):
            self.VK_MAP[i] = chr(i).lower()

        for i in range(ord('0'), ord('9') + 1):
            self.VK_MAP[i] = chr(i)

        # 添加特殊字符
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

        # 启动滚轮监听
        self.start_wheel_listener()

    def cleanup(self):
        self.stop_wheel_listener()
        try:
            pydirectinput.releaseAll()
        except:
            pass
        self.mouse_buttons = {k: False for k in self.mouse_buttons}
        self.prev_mouse_buttons = self.mouse_buttons.copy()
        self.key_states = {}
        self.prev_key_states = {}
        self.wheel_delta = 0

    def stop_wheel_listener(self):
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            # 强制等待线程退出
            for _ in range(3):  # 重试3次
                if self.mouse_listener.is_alive():
                    self.mouse_listener.join(timeout=0.5)
                else:
                    break
            self.mouse_listener = None  # 置空，避免重复操作

    def _on_scroll(self, x, y, dx, dy):
        """pynput滚轮事件回调函数"""
        with self.wheel_lock:
            self.wheel_delta += dy * 120

    def start_wheel_listener(self):
        """启动pynput滚轮监听器"""
        if self.mouse_listener is None or not self.mouse_listener.is_alive():
            self.mouse_listener = mouse.Listener(
                on_scroll=self._on_scroll,
                on_move=None,
                on_click=None
            )
            self.mouse_listener.start()

    def update(self):
        """更新所有输入状态并保存上一帧状态"""
        # 保存当前状态到上一帧状态
        self.prev_mouse_buttons = self.mouse_buttons.copy()
        self.prev_key_states = self.key_states.copy()

        # 更新当前状态
        self._update_mouse_state()
        self._update_keyboard_state()
        self._update_mouse_position()

    def _update_mouse_state(self):
        """更新鼠标按钮状态"""
        self.mouse_buttons["LMB"] = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0
        self.mouse_buttons["RMB"] = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0
        self.mouse_buttons["MMB"] = win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0
        self.mouse_buttons["XMB1"] = win32api.GetAsyncKeyState(0x05) < 0  # VK_XBUTTON1
        self.mouse_buttons["XMB2"] = win32api.GetAsyncKeyState(0x06) < 0  # VK_XBUTTON2

    def _update_keyboard_state(self):
        """更新键盘按键状态"""
        for vk_code, key_name in self.VK_MAP.items():
            state = win32api.GetAsyncKeyState(vk_code)
            self.key_states[key_name] = (state & 0x8000) != 0

    def _update_mouse_position(self):
        """更新鼠标位置"""
        try:
            self.mouse_x, self.mouse_y = win32api.GetCursorPos()
        except:
            pass

    # ===== 状态检测方法 =====
    def is_mouse_pressing(self, button_name):
        """检测鼠标按钮当前是否按下（当前帧按下）"""
        if isinstance(button_name, str):
            button = button_name.upper()
            return self.mouse_buttons.get(button, False)
        return False

    def is_mouse_pressed(self, button_name):
        """检测鼠标按钮是否刚刚按下（上一帧未按下，当前帧按下）"""
        if isinstance(button_name, str):
            button = button_name.upper()
            return self.mouse_buttons.get(button, False) and \
                   not self.prev_mouse_buttons.get(button, False)
        return False

    def is_mouse_released(self, button_name):
        """检测鼠标按钮是否刚刚释放（上一帧按下，当前帧未按下）"""
        if isinstance(button_name, str):
            button = button_name.upper()
            return not self.mouse_buttons.get(button, False) and \
                   self.prev_mouse_buttons.get(button, False)
        return False

    def is_key_presssing(self, key_name):
        """检测键盘按键当前是否按下（当前帧按下）"""
        if isinstance(key_name, str):
            return self.key_states.get(key_name.lower(), False)
        if isinstance(key_name, int):
            key_name = self.VK_MAP.get(key_name, None)
            if key_name:
                return self.key_states.get(key_name, False)
        return False

    def is_key_pressed(self, key_name):
        """检测键盘按键是否刚刚按下（上一帧未按下，当前帧按下）"""
        if isinstance(key_name, str):
            key = key_name.lower()
            return self.key_states.get(key, False) and \
                   not self.prev_key_states.get(key, False)
        if isinstance(key_name, int):
            key_name = self.VK_MAP.get(key_name, None)
            if key_name:
                key = key_name.lower()
                return self.key_states.get(key, False) and \
                       not self.prev_key_states.get(key, False)
        return False

    def is_key_released(self, key_name):
        """检测键盘按键是否刚刚释放（上一帧按下，当前帧未按下）"""
        if isinstance(key_name, str):
            key = key_name.lower()
            return not self.key_states.get(key, False) and \
                   self.prev_key_states.get(key, False)
        if isinstance(key_name, int):
            key_name = self.VK_MAP.get(key_name, None)
            if key_name:
                key = key_name.lower()
                return not self.key_states.get(key, False) and \
                       self.prev_key_states.get(key, False)
        return False

    def is_pressed(self, name):
        if self.is_key_pressed(name) or self.is_mouse_pressed(name):
            return True
        return False

    def is_pressing(self, name):
        if self.is_key_presssing(name) or self.is_mouse_pressing(name):
            return True
        return False

    def is_released(self, name):
        if self.is_key_released(name) or self.is_mouse_released(name):
            return True
        return False

    def alt_ctrl_shift(self, alt: bool=False, ctrl: bool=False, shift: bool=False):
        if self.is_key_presssing('alt') == alt\
            and self.is_key_presssing('ctrl') == ctrl\
                and self.is_key_presssing('shift') == shift:
            return True
        else:
            return False

    def is_hotkey_pressed(self, hotkey_str):
        modifiers, main_key = self.parse_hotkey(hotkey_str)

        ctrl_ok = ('ctrl' in modifiers) == self.is_key_presssing('ctrl')
        alt_ok = ('alt' in modifiers) == self.is_key_presssing('alt')
        shift_ok = ('shift' in modifiers) == self.is_key_presssing('shift')

        if not (ctrl_ok and alt_ok and shift_ok):
            return False

        return self.is_pressed(main_key)

    def get_mouse_position(self):
        return self.mouse_x, self.mouse_y

    def set_mouse_position(self, x, y):
        try:
            for _ in range(self.retry):
                pydirectinput.moveTo(pos(x), pos(y), duration=0)
            self._update_mouse_position()
        except Exception as e:
            print(e)

    def get_mouse_delta(self, prev_x, prev_y):
        return self.mouse_x - prev_x, self.mouse_y - prev_y

    def get_wheel_delta(self):
        with self.wheel_lock:
            delta = self.wheel_delta
            self.wheel_delta = 0
        return delta

    def reset_wheel_delta(self):
        with self.wheel_lock:
            self.wheel_delta = 0

    def parse_hotkey(self, hotkey_str):
        """解析组合键字符串"""
        keys = hotkey_str.split('+')
        modifiers = []
        main_key = None

        for key in keys:
            normalized = key.strip().lower()
            if normalized in ['ctrl', 'control']:
                modifiers.append('ctrl')
            elif normalized == 'alt':
                modifiers.append('alt')
            elif normalized == 'shift':
                modifiers.append('shift')
            else:
                main_key = normalized

        return modifiers, main_key

    def __del__(self):
        self.stop_wheel_listener()
