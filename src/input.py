import threading
import time

import pydirectinput
import win32api
import win32con

from lib.axis import pos
from loguru import logger


class InputStateMonitor:
    def __init__(self, pause=0.016, retry=2):
        self.pause = pause
        self.retry = retry

        pydirectinput.PAUSE = self.pause
        pydirectinput.FAILSAFE = False

        self.mouse_buttons = {
            'LMB': False,
            'RMB': False,
            'MMB': False,
            'XMB1': False,  # 侧键1 (前进)
            'XMB2': False,  # 侧键2 (后退)
            'XMB3': False,  # 侧键3
            'XMB4': False,  # 侧键4
            'XMB5': False,  # 侧键5
            'XMB6': False,  # 侧键6
            'XMB7': False,  # 侧键7
            'XMB8': False,  # 侧键8
        }
        self.prev_mouse_buttons = self.mouse_buttons.copy()

        self.key_states = {}
        self.prev_key_states = {}

        self.mouse_x = 0
        self.mouse_y = 0

        self.wheel_delta = 0
        self.wheel_lock = threading.Lock()

        self.VK_MAP = {
            win32con.VK_SHIFT: 'shift',
            win32con.VK_CONTROL: 'ctrl',
            win32con.VK_MENU: 'alt',
            win32con.VK_SPACE: 'space',
            win32con.VK_RETURN: 'enter',
            win32con.VK_ESCAPE: 'esc',
            win32con.VK_TAB: 'tab',
            win32con.VK_CAPITAL: 'capslock',
            win32con.VK_BACK: 'backspace',
            win32con.VK_INSERT: 'insert',
            win32con.VK_DELETE: 'delete',
            win32con.VK_HOME: 'home',
            win32con.VK_END: 'end',
            win32con.VK_PRIOR: 'pageup',
            win32con.VK_NEXT: 'pagedown',
            win32con.VK_LWIN: 'win',
            win32con.VK_UP: 'up',
            win32con.VK_DOWN: 'down',
            win32con.VK_LEFT: 'left',
            win32con.VK_RIGHT: 'right',
            win32con.VK_F1: 'f1',
            win32con.VK_F2: 'f2',
            win32con.VK_F3: 'f3',
            win32con.VK_F4: 'f4',
            win32con.VK_F5: 'f5',
            win32con.VK_F6: 'f6',
            win32con.VK_F7: 'f7',
            win32con.VK_F8: 'f8',
            win32con.VK_F9: 'f9',
            win32con.VK_F10: 'f10',
            win32con.VK_F11: 'f11',
            win32con.VK_F12: 'f12',
            win32con.VK_SNAPSHOT: 'snapshot',
            win32con.VK_SCROLL: 'scrolllock',
            win32con.VK_PAUSE: 'pause',
            win32con.VK_NUMLOCK: 'numlock',
        }

        for i in range(ord('A'), ord('Z') + 1):
            self.VK_MAP[i] = chr(i).lower()

        for i in range(ord('0'), ord('9') + 1):
            self.VK_MAP[i] = chr(i)

        special_chars = {
            0xBA: ';',
            0xBB: '=',
            0xBC: ',',
            0xBD: '-',
            0xBE: '.',
            0xBF: '/',
            0xC0: '`',
            0xDB: '[',
            0xDC: '\\',
            0xDD: ']',
            0xDE: "'",
        }
        self.VK_MAP.update(special_chars)

    def start(self):
        # 移除钩子线程，因为我们已经在main.py的nativeEvent中处理滚轮事件
        pass

    def stop(self):
        # 移除钩子线程相关代码
        pass

    def cleanup(self):
        self.mouse_buttons = {k: False for k in self.mouse_buttons}
        self.prev_mouse_buttons = self.mouse_buttons.copy()
        self.key_states = {}
        self.prev_key_states = {}
        with self.wheel_lock:
            self.wheel_delta = 0

    def update(self):
        self.prev_mouse_buttons = self.mouse_buttons.copy()
        self.prev_key_states = self.key_states.copy()
        self._update_mouse_state()
        self._update_keyboard_state()
        self._update_mouse_position()

    def _update_mouse_state(self):
        self.mouse_buttons['LMB'] = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0
        self.mouse_buttons['RMB'] = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0
        self.mouse_buttons['MMB'] = win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0
        self.mouse_buttons['XMB1'] = win32api.GetAsyncKeyState(0x05) < 0
        self.mouse_buttons['XMB2'] = win32api.GetAsyncKeyState(0x06) < 0

    def _update_keyboard_state(self):
        for vk_code, key_name in self.VK_MAP.items():
            self.key_states[key_name] = (win32api.GetAsyncKeyState(vk_code) & 0x8000) != 0

    def _update_mouse_position(self):
        try:
            self.mouse_x, self.mouse_y = win32api.GetCursorPos()
        except Exception as e:
            logger.exception(f'Failed to get cursor position: {str(e)}')

    def is_mouse_pressing(self, button_name):
        if isinstance(button_name, str):
            return self.mouse_buttons.get(button_name.upper(), False)
        return False

    def is_mouse_pressed(self, button_name):
        if isinstance(button_name, str):
            button = button_name.upper()
            return self.mouse_buttons.get(button, False) and not self.prev_mouse_buttons.get(button, False)
        return False

    def is_mouse_released(self, button_name):
        if isinstance(button_name, str):
            button = button_name.upper()
            return not self.mouse_buttons.get(button, False) and self.prev_mouse_buttons.get(button, False)
        return False

    def is_key_pressing(self, key_name):
        if isinstance(key_name, str):
            return self.key_states.get(key_name.lower(), False)
        if isinstance(key_name, int):
            mapped = self.VK_MAP.get(key_name)
            if mapped:
                return self.key_states.get(mapped, False)
        return False

    def is_key_pressed(self, key_name):
        if isinstance(key_name, str):
            key = key_name.lower()
            return self.key_states.get(key, False) and not self.prev_key_states.get(key, False)
        if isinstance(key_name, int):
            mapped = self.VK_MAP.get(key_name)
            if mapped:
                return self.key_states.get(mapped, False) and not self.prev_key_states.get(mapped, False)
        return False

    def is_key_released(self, key_name):
        if isinstance(key_name, str):
            key = key_name.lower()
            return not self.key_states.get(key, False) and self.prev_key_states.get(key, False)
        if isinstance(key_name, int):
            mapped = self.VK_MAP.get(key_name)
            if mapped:
                return not self.key_states.get(mapped, False) and self.prev_key_states.get(mapped, False)
        return False

    def is_pressed(self, name):
        return self.is_key_pressed(name) or self.is_mouse_pressed(name)

    def is_pressing(self, name):
        return self.is_key_pressing(name) or self.is_mouse_pressing(name)

    def is_released(self, name):
        return self.is_key_released(name) or self.is_mouse_released(name)

    def alt_ctrl_shift(self, alt: bool = False, ctrl: bool = False, shift: bool = False):
        return (
            self.is_key_pressing('alt') == alt
            and self.is_key_pressing('ctrl') == ctrl
            and self.is_key_pressing('shift') == shift
        )

    def is_hotkey_pressed(self, hotkey_str):
        modifiers, main_key = self.parse_hotkey(hotkey_str)
        if not (
            ('ctrl' in modifiers) == self.is_key_pressing('ctrl')
            and ('alt' in modifiers) == self.is_key_pressing('alt')
            and ('shift' in modifiers) == self.is_key_pressing('shift')
        ):
            return False
        return self.is_pressed(main_key)

    def get_mouse_position(self):
        return self.mouse_x, self.mouse_y

    def set_mouse_position(self, x, y):
        try:
            for _ in range(self.retry):
                pydirectinput.moveTo(pos(x), pos(y), duration=0)
                time.sleep(self.pause)
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