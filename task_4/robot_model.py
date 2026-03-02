import math
from dataclasses import dataclass
from enum import StrEnum


class CleaningMode(StrEnum):
    WATER = "water"
    SOAP = "soap"
    BRUSH = "brush"


@dataclass
class Robot:
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    mode: CleaningMode = CleaningMode.WATER

    def reset(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.mode = CleaningMode.WATER

    def move(self, dist: float) -> None:
        angle_rads = self.angle * (math.pi / 180.0)
        self.x += dist * math.cos(angle_rads)
        self.y += dist * math.sin(angle_rads)

    def turn(self, delta: int) -> None:
        self.angle += delta

    def set_mode(self, mode: CleaningMode) -> None:
        self.mode = mode
