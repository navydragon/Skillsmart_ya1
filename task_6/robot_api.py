# Понял задачу так: нам нужно дать внешнему коду простой интерфейс с роботу, код которого уже существует
# (pure_robot), который полностью прячет внутри себя pure_robot: снаружи видны только методы,
# исполнение текстовых команд и геттеры , а детали вроде RobotState не смотрят "наружу" и их можно менять
# без ущерба для клиентов 


from collections.abc import Iterable
from . import pure_robot


class RobotAPI:

    def __init__(self, transfer=pure_robot.transfer_to_cleaner) -> None:
        self._transfer = transfer
        self._state = pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)

    # параметры
    @property
    def x(self) -> float:
        return self._state.x

    @property
    def y(self) -> float:
        return self._state.y

    @property
    def angle(self) -> float:
        return self._state.angle

    # операции
    def reset(self) -> None:
        self._state = pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)

    def move(self, distance: float) -> None:
        self._state = pure_robot.move(self._transfer, distance, self._state)

    def turn(self, delta: float) -> None:
        self._state = pure_robot.turn(self._transfer, delta, self._state)

    def set_mode(self, mode: str) -> None:
        self._state = pure_robot.set_state(self._transfer, mode, self._state)

    def start(self) -> None:
        self._state = pure_robot.start(self._transfer, self._state)

    def stop(self) -> None:
        self._state = pure_robot.stop(self._transfer, self._state)

    # обработка текстовой команды
    def execute_command(self, command: str) -> None:
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        if cmd == "move" and args:
            self.move(float(args[0]))
        elif cmd == "turn" and args:
            self.turn(float(args[0]))
        elif cmd == "set" and args:
            self.set_mode(args[0])
        elif cmd == "start":
            self.start()
        elif cmd == "stop":
            self.stop()

    def run_program(self, commands: Iterable[str]) -> None:
        self.reset()
        for command in commands:
            self.execute_command(command)

