from collections.abc import Iterable
from typing import Callable

from robot_logging import RobotLogger
from robot_model import Robot, CleaningMode


class RobotController:
    def __init__(self, robot: Robot, logger: RobotLogger | None = None) -> None:
        self._robot = robot
        self._logger = logger or RobotLogger()
        self._actions: dict[str, Callable[[list[str]], None]] = {
            "move": self._handle_move,
            "turn": self._handle_turn,
            "set": self._handle_set,
            "start": self._handle_start,
            "stop": self._handle_stop,
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
                self._logger.log_unknown_command(cmd)
        except (IndexError, ValueError) as error:
            self._logger.log_error(error)

    def run_program(self, commands: Iterable[str]) -> None:
        self._robot.reset()
        for command in commands:
            self.execute_command(command)

    def _handle_move(self, args: list[str]) -> None:
        distance = float(args[0])
        self._robot.move(distance)
        self._logger.log_position(self._robot.x, self._robot.y)

    def _handle_turn(self, args: list[str]) -> None:
        delta = int(args[0])
        self._robot.turn(delta)
        self._logger.log_angle(self._robot.angle)

    def _handle_set(self, args: list[str]) -> None:
        mode_name = args[0]
        try:
            mode = CleaningMode(mode_name)
        except ValueError:
            self._logger.log_unknown_mode(mode_name)
            return

        self._robot.set_mode(mode)
        self._logger.log_state(self._robot.mode.value)

    def _handle_start(self, args: list[str]) -> None:  # noqa: ARG002
        self._logger.log_start(self._robot.mode.value)

    def _handle_stop(self, args: list[str]) -> None:  # noqa: ARG002
        self._logger.log_stop()

