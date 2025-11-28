import threading


class EventEmitter:
    def __init__(self):
        self.events = {}
        self.lock = threading.Lock()

    def on(self, event_name, handler):
        with self.lock:
            if event_name not in self.events:
                self.events[event_name] = []
            if handler not in self.events[event_name]:
                self.events[event_name].append(handler)

    def once(self, event_name, handler):
        def wrapper(*args, **kwargs):
            handler(*args, **kwargs)
            self.off(event_name, wrapper)

        self.on(event_name, wrapper)
        return wrapper

    def emit(self, event_name, *args, **kwargs):
        with self.lock:
            if event_name not in self.events:
                return
            handlers = list(self.events[event_name])

        for handler in handlers:
            handler(*args, **kwargs)

    def off(self, event_name, handler=None):
        with self.lock:
            if event_name is None:
                self.events.clear()
                return

            if event_name not in self.events:
                return

            if handler is None:
                self.events[event_name] = []
            else:
                if handler in self.events[event_name]:
                    self.events[event_name].remove(handler)

    def get_handlers(self, event_name):
        with self.lock:
            return self.events.get(event_name, [])
