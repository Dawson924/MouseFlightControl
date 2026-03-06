from typing import Dict, Optional

from common.axis import AxisName


class Filter:
    def __init__(
        self,
        invert: Optional[bool] = None,
        curvature: Optional[float] = None,
        deadzone: Optional[int] = None,
        preset: Optional[str] = None,
        smooth: Optional[int] = None,
    ):
        self.invert = invert
        self.curvature = curvature
        self.deadzone = deadzone
        self.preset = preset
        self.smooth = smooth

    def to_dict(self) -> Dict:
        return {key: value for key, value in self.__dict__.items() if value is not None}

    @classmethod
    def from_dict(cls, data: Dict) -> 'Filter':
        valid_keys = ['invert', 'curvature', 'deadzone', 'preset', 'smooth']
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


Filters = Dict[AxisName, Filter]
