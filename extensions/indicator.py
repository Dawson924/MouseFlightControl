from plugin.runtime import Extension


class Plugin(Extension):
    id = 'indicator'
    name = 'Axis Indicator'
    version = '1.0.0'

    def get_default_config(self):
        return {
            'indicator_x': 50,
            'indicator_y': -50,
            'indicator_size': 250
        }

    def __init__(self):
        self._config = {}
        self._runtime = None
        self._indicator = None

    def setup(self, runtime) -> None:
        self._runtime = runtime
        self._indicator = runtime.indicator
        self._config = runtime.load_settings(self.id)
        if not self._config:
            self._config = self.get_default_config()

        self.apply_indicator()

    def apply_indicator(self) -> None:
        if not self._indicator:
            return

        x = self._config.get('indicator_x')
        y = self._config.get('indicator_y')
        size = self._config.get('indicator_size')

        self._indicator.set_position(x, y)
        self._indicator.set_size(size)
