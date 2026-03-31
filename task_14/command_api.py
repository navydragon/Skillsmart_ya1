# Задача реализовать Command для pure_robot 
# идея, что в Command "действие" становится объектом, и у этого объекта появляется единый интерфейс (execute)
# мне понравилась: один класс = одна команда. Для понимания просто, нет elif и минимум мутабельного состояния!
# С другой стороны, если у нас объекты это классы, действия это классы, то легко запутаться
# В ФП-подобных заданиях курса это как будто лучше было разделено - функции (действия) и данные (объекты).

# Invoker - это герой в доте (зачеркнуто) RobotAPI, 
# Command -  классы Batch, Move, Turn, SetMode, Start, Stop
# Receiver -  pure_robot
# Client -  client.py

from dataclasses import dataclass
from . import pure_robot

State = pure_robot.RobotState


@dataclass(frozen=True, slots=True)
class Move:
    dist: int 

    def execute(self, transfer, state):
        return pure_robot.move(transfer, self.dist, state)


@dataclass(frozen=True, slots=True)
class Turn:
    angle: int

    def execute(self, transfer, state):
        return pure_robot.turn(transfer, self.angle, state)


@dataclass(frozen=True, slots=True)
class SetMode:
    mode: str  # "water" | "soap" | "brush"

    def execute(self, transfer, state):
        return pure_robot.set_state(transfer, self.mode, state)


@dataclass(frozen=True, slots=True)
class Start:
    def execute(self, transfer, state):
        return pure_robot.start(transfer, state)


@dataclass(frozen=True, slots=True)
class Stop:
    def execute(self, transfer, state):
        return pure_robot.stop(transfer, state)


@dataclass(frozen=True, slots=True)
class Batch:

    commands: tuple

    def __post_init__(self):
        # Нормализуем и валидируем "пачку":
        # - разворачиваем вложенные Batch
        # - проверяем, что каждый элемент похож на команду (есть execute)
        flat = []
        for i, cmd in enumerate(self.commands):
            if isinstance(cmd, Batch):
                flat.extend(cmd.commands)
                continue
            if not hasattr(cmd, "execute") or not callable(getattr(cmd, "execute")):
                raise TypeError(
                    f"Batch: элемент #{i} не является командой (нет метода execute): {cmd!r}"
                )
            flat.append(cmd)
        object.__setattr__(self, "commands", tuple(flat))

    def execute(self, transfer, state):
        for i, cmd in enumerate(self.commands):
            try:
                state = cmd.execute(transfer, state)
            except Exception as e:
                raise RuntimeError(
                    f"Batch: ошибка на шаге #{i} ({cmd.__class__.__name__})"
                ) from e
        return state


class RobotApi:

    def setup(self, transfer):
        self.transfer = transfer

    def make(self, program, state=None):
        if state is None:
            state = pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)

        # Разрешаем передать как одну команду, так и список/Batch.
        if hasattr(program, "execute") and callable(getattr(program, "execute")):
            return program.execute(self.transfer, state)

        for i, cmd in enumerate(program):
            if not hasattr(cmd, "execute") or not callable(getattr(cmd, "execute")):
                raise TypeError(
                    f"RobotApi: элемент программы #{i} не является командой: {cmd!r}"
                )
            state = cmd.execute(self.transfer, state)
        return state

    def __call__(self, program, state=None):
        return self.make(program, state)


api = RobotApi()
api.setup(pure_robot.transfer_to_cleaner)

