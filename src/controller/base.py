from abc import ABC, abstractmethod


class BaseController(ABC):
    def __init__(self, vjoy):
        self.vjoy = vjoy

    @abstractmethod
    def update(self, state, context):
        return
