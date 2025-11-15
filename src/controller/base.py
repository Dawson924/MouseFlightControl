from abc import ABC, abstractmethod


class BaseController(ABC):
    def __init__(self, device):
        self.device = device

    @abstractmethod
    def update(self, Axis, options, input, state, context):
        return
