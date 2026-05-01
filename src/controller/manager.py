from controller.base import BaseController


class FlightControllers:
    def __init__(self):
        self.controllers = {}
        self.metadata = {}
        self._controller = None
        self._flight_mode = None

    def register(self, id: int, controller_class: BaseController, metadata=None):
        self.controllers[id] = controller_class
        self.metadata[id] = metadata or {}

    def get_class(self, id):
        return self.controllers.get(id)

    def get_metadata(self, id):
        return self.metadata.get(id, {})

    def get_name(self, id):
        metadata = self.get_metadata(id)
        return metadata['name']

    def ids(self):
        return list(self.controllers.keys())

    def names(self):
        return [item['name'] for item in self.metadata.values()]

    def update(self, flightdata):
        flight_mode = flightdata['Input']['flight_mode']
        if flight_mode != self._flight_mode:
            self._flight_mode = flight_mode
            Class = self.get_class(flight_mode)
            if Class:
                self._controller = Class(flightdata)
            else:
                self._controller = None
        return self._controller
