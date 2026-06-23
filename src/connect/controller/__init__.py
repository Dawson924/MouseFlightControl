from .aircraft import Controller, HelicopterController, JetPlaneController, PistonPlaneController


class FlightControllers:
    def __init__(self):
        self._registry = {}
        self._metadata = {}
        self._controller: Controller = None
        self._model = None
        self._flight_mode = None

    def register(self, id: int, controller_class: Controller, metadata=None):
        self._registry[id] = controller_class
        self._metadata[id] = metadata or {}

    def get_class(self, id):
        return self._registry.get(id)

    def get_metadata(self, id):
        return self._metadata.get(id, {})

    def get_name(self, id):
        metadata = self.get_metadata(id)
        return metadata['name']

    def ids(self):
        return list(self._registry.keys())

    def names(self):
        return [item['name'] for item in self._metadata.values()]

    def refresh_fields(self):
        if self._controller is not None:
            self._controller._load_fields()

    def update(self, flightinput):
        model = flightinput['Connect']['model']
        flight_mode = flightinput['Input']['flight_mode']
        if model != self._model or flight_mode != self._flight_mode:
            self._model = model
            self._flight_mode = flight_mode
            Class = self.get_class(flight_mode)
            if Class:
                self._controller = Class(flightinput)
            else:
                self._controller = None

        return self._controller


controllers = FlightControllers()

controllers.register(
    1,
    JetPlaneController,
    {'name': 'Fixed Wing'},
)
controllers.register(
    2,
    HelicopterController,
    {'name': 'Helicopter'},
)
controllers.register(
    3,
    PistonPlaneController,
    {'name': 'Piston Plane'},
)

__all__ = ['controllers']
