from win32 import get_mouse_speed, set_mouse_speed

from plugin.runtime import Extension, RuntimeContext


class Plugin(Extension):
    id = 'speed_adjuster'
    name = 'Speed Adjuster'

    def get_default_config(self):
        return {
            'toggle_key': 'shift + `'
        }

    def setup(self, runtime: RuntimeContext):
        self.runtime = runtime
        self.original_speed = None
        self.is_active = False

        config = runtime.load_settings(self.id)
        if not config:
            config = self.get_default_config()
        self.toggle_key = config.get('toggle_key')

        runtime.on('tick', self._on_tick)

    def _on_tick(self, dt: float):
        input = self.runtime.input

        if not input:
            return

        if input.is_hotkey_pressed(self.toggle_key):
            self._toggle()

    def _toggle(self):
        if self.is_active:
            self._disable()
        else:
            self._enable()

    def _enable(self):
        if self.original_speed is None:
            self.original_speed = get_mouse_speed()

        new_speed = int(self.original_speed * 2.5)
        set_mouse_speed(new_speed)
        self.is_active = True

    def _disable(self):
        if self.original_speed is not None:
            set_mouse_speed(self.original_speed)
            self.is_active = False

    def teardown(self):
        if self.is_active:
            self._disable()