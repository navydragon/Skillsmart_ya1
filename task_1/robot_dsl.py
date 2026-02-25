# На что старался делать упор при разработке:
# не писать повторяющийся код: RobotState изменяется с помощью replace
# не использовать "магические значния" для CleaningMode, вынес в отдельный класс
# вынести все возможные команды робота в словарь _handlers, чтобы не писать if/elif в execute_command
# отделить проверку предусловий команды и ее выполнение
# при ошибке в команде программа не должна вылетать, а делать print ошибки и идти дальше

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable


class CleaningMode(str, Enum):
    WATER = "water"
    SOAP = "soap"
    BRUSH = "brush"


@dataclass(frozen=True)
class RobotState:
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0  # в градусах, 0 — направление вправо
    mode: CleaningMode = CleaningMode.WATER
    is_running: bool = False


def _format_number(value: float) -> str:

    if abs(value) < 1e-9:
        value = 0.0
    rounded = round(value, 2)
    if rounded.is_integer():
        return str(int(rounded))

    s = f"{rounded:.2f}"
    s = s.rstrip("0").rstrip(".")
    return s


class Robot:
    def __init__(self, state: RobotState | None = None) -> None:
        self.state: RobotState = state or RobotState()
        self._handlers = {
            "move": self._handle_move,
            "turn": self._handle_turn,
            "set": self._handle_set,
            "start": self._handle_start,
            "stop": self._handle_stop,
        }

    # Публичные методы
    def move(self, distance: float) -> None:
        angle_rad = math.radians(self.state.angle)
        dx = distance * math.cos(angle_rad)
        dy = distance * math.sin(angle_rad)
        new_state = replace(self.state, x=self.state.x + dx, y=self.state.y + dy)
        self.state = new_state
        print(f"POS {_format_number(new_state.x)},{_format_number(new_state.y)}")

    def turn(self, delta_angle: float) -> None:
        new_angle = (self.state.angle + delta_angle) % 360
        new_state = replace(self.state, angle=new_angle)
        self.state = new_state
        print(f"ANGLE {_format_number(new_state.angle)}")

    def set_mode(self, mode: str) -> None:
        mode_str = mode.lower()
        try:
            new_mode = CleaningMode(mode_str)
        except ValueError as exc:
            raise ValueError(f"неизвестный режим очистки: {mode_str}") from exc
        new_state = replace(self.state, mode=new_mode)
        self.state = new_state
        print(f"STATE {new_state.mode.value}")

    def start(self) -> None:
        new_state = replace(self.state, is_running=True)
        self.state = new_state
        print(f"START WITH {new_state.mode.value}")

    def stop(self) -> None:
        new_state = replace(self.state, is_running=False)
        self.state = new_state
        print("STOP")

    def _handle_move(self, args: list[str]) -> None:
        if len(args) != 1:
            raise ValueError(f"команда move ожидает 1 аргумент, получено {len(args)}")
        distance = float(args[0])
        self.move(distance)

    def _handle_turn(self, args: list[str]) -> None:
        if len(args) != 1:
            raise ValueError(f"команда turn ожидает 1 аргумент, получено {len(args)}")
        delta = float(args[0])
        self.turn(delta)

    def _handle_set(self, args: list[str]) -> None:
        if len(args) != 1:
            raise ValueError(f"команда set ожидает 1 аргумент, получено {len(args)}")
        mode = args[0]
        self.set_mode(mode)

    def _handle_start(self, args: list[str]) -> None:
        if args:
            raise ValueError("команда start не принимает аргументов")
        self.start()

    def _handle_stop(self, args: list[str]) -> None:
        if args:
            raise ValueError("команда stop не принимает аргументов")
        self.stop()

    def execute_command(self, command_str: str) -> None:
        parts = command_str.strip().split()
        if not parts:
            return

        try:
            cmd = parts[0].lower()
            args = parts[1:]

            handler = self._handlers.get(cmd)
            if handler is None:
                raise ValueError(f"неизвестная команда: {cmd}")

            handler(args)
        except Exception as exc:
            print(f"ОШИБКА {exc}")


def run_program(commands: Iterable[str]) -> None:
    robot = Robot()
    for command in commands:
        robot.execute_command(command)


if __name__ == "__main__":
    input = [
        "move 100",
        "turn -90",
        "set soap",
        "start",
        "move 50",
        "stop",
    ]
    run_program(input)

