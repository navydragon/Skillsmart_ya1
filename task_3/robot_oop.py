# как я понял эту задачу (т.к. по сути в задании 1 у меня был тоже ООП)
# у нас есть в качестве исходного "процедурный вариант" робота
# и нам надо попытаться реализовать как можно более "чистый ООП"
# Что я постарался применить:
# -Композицию с классом CleaningMode (была в задании 1)
# -Композицию с классом RobotLogger (не было в задании 1) - теперь методы робота сами не печатают
# -т.к. "все ООП", то добавил RobotController, который и управляет процессом
# -очень хотел уйти от кучи доп фугкций а-ля _handle_move, в итоге "подсмотрел" вариант с lambda args ...
# -стало короче, но теперь вся валидация на try/except :(
# -а если бы были доменные ограничения, то их вероятно стоило бы записать в сам Robot


import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Iterable, Optional


class CleaningMode(IntEnum):
    WATER = 1  # полив водой
    SOAP = 2   # полив мыльной пеной
    BRUSH = 3  # чистка метлой


class RobotLogger:
    def log_position(self, x: float, y: float) -> None:
        print("POS(", x, ",", y, ")")

    def log_angle(self, angle: float) -> None:
        print("ANGLE", angle)

    def log_state(self, state: int) -> None:
        print("STATE", state)

    def log_start(self, mode: int) -> None:
        print("START WITH", mode)

    def log_stop(self) -> None:
        print("STOP")

    def log_unknown_mode(self, mode_name: str) -> None:
        print("ОШИБКА неизвестный режим:", mode_name)

    def log_unknown_command(self, cmd: str) -> None:
        print("ОШИБКА неизвестная команда:", cmd)

    def log_error(self, error: Exception) -> None:
        print("ОШИБКА", error)


@dataclass
class Robot:
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0
    mode: CleaningMode = CleaningMode.WATER
    logger: Optional[RobotLogger] = None

    def reset(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.mode = CleaningMode.WATER

    def move(self, dist: float) -> None:
        angle_rads = self.angle * (math.pi / 180.0)
        self.x += dist * math.cos(angle_rads)
        self.y += dist * math.sin(angle_rads)
        if self.logger is not None:
            self.logger.log_position(self.x, self.y)

    def turn(self, delta: int) -> None:
        self.angle += delta
        if self.logger is not None:
            self.logger.log_angle(self.angle)

    def set_mode(self, mode_name: str) -> None:
        normalized = mode_name.lower()
        modes = {
            "water": CleaningMode.WATER,
            "soap": CleaningMode.SOAP,
            "brush": CleaningMode.BRUSH,
        }
        mode = modes.get(normalized)
        if mode is None:
            if self.logger is not None:
                self.logger.log_unknown_mode(mode_name)
            return
        self.mode = mode
        if self.logger is not None:
            self.logger.log_state(int(self.mode))

    def start(self) -> None:
        if self.logger is not None:
            self.logger.log_start(int(self.mode))

    def stop(self) -> None:
        if self.logger is not None:
            self.logger.log_stop()


class RobotController:
    def __init__(self, robot: Robot, logger: Optional[RobotLogger] = None) -> None:
        self._robot = robot
        self._logger = logger or robot.logger
        self._actions: dict[str, Callable[[list[str]], None]] = {
            "move": lambda args: self._robot.move(float(args[0])),
            "turn": lambda args: self._robot.turn(int(args[0])),
            "set": lambda args: self._robot.set_mode(args[0]),
            "start": lambda args: self._robot.start(),
            "stop": lambda args: self._robot.stop(),
        }

    def execute_command(self, command: str) -> None:
        parts = command.split()
        if not parts:
            return

        cmd, *args = parts
        handler = self._actions.get(cmd)

        try:
            if handler is not None:
                handler(args)
            else:
                if self._logger is not None:
                    self._logger.log_unknown_command(cmd)
        except (IndexError, ValueError) as e:
            if self._logger is not None:
                self._logger.log_error(e)

    def run_program(self, code: Iterable[str]) -> None:
        self._robot.reset()
        for command in code:
            self.execute_command(command)


def main() -> None:
    logger = RobotLogger()
    robot = Robot(logger=logger)
    controller = RobotController(robot, logger=logger)
    program = [
        "move 100",
        "turn -90",
        "set soap",
        "start",
        "move 50",
        "stop",
    ]
    controller.run_program(program)


if __name__ == "__main__":
    main()

