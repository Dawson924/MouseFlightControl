from typing import Tuple

from common.axis import AXIS_MAX
from lib.win32 import get_screen_geometry


class Screen:
    def __init__(self, window_handle: int, screen_object):
        try:
            (
                self.screen_width,
                self.screen_height,
                self.center_x,
                self.center_y,
                self.scale,
            ) = get_screen_geometry(window_handle, screen_object)
        except Exception as e:
            from lib.logger import logger

            logger.error(f'Failed to get screen geometry: {e}')
            self.screen_width = 1920
            self.screen_height = 1080
            self.center_x = 960
            self.center_y = 540
            self.scale = 1.0

    def to_pixels(self, pt: int) -> int:
        return int(pt * self.scale)

    def axis_to_screen(self, axis_x: float, axis_y: float) -> Tuple[float, float]:
        x_percent = axis_x / AXIS_MAX
        y_percent = axis_y / AXIS_MAX

        screen_x = self.center_x + x_percent * (self.screen_width / 2)
        screen_y = self.center_y + y_percent * (self.screen_height / 2)

        return screen_x, screen_y

    def screen_to_axis(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        x_percent = (screen_x - self.center_x) / (self.screen_width / 2)
        y_percent = (screen_y - self.center_y) / (self.screen_height / 2)

        axis_x = x_percent * AXIS_MAX
        axis_y = y_percent * AXIS_MAX

        return axis_x, axis_y

    def screen_geometry(self) -> Tuple[int, int, float, float, float]:
        return (self.screen_width, self.screen_height, self.center_x, self.center_y, self.scale)

    def aspect_ratio(self) -> float:
        if self.screen_height == 0:
            return 1.0
        return self.screen_width / self.screen_height

    def normalize(self, x: float, y: float) -> Tuple[float, float]:
        norm_x = (x - self.center_x) / (self.screen_width / 2)
        norm_y = (y - self.center_y) / (self.screen_height / 2)

        return norm_x, norm_y
