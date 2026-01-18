from dataclasses import dataclass
from typing import Optional


@dataclass
class Filter:
    invert: Optional[bool] = None
    curvature: Optional[float] = None
    deadzone: Optional[int] = None
    smooth_preset: Optional[str] = None
    smooth_speed: Optional[int] = None
