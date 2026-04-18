import math
from collections import namedtuple
from dataclasses import dataclass

RobotState = namedtuple("RobotState", "x y angle state")

# режимы работы устройства очистки
WATER = 1  # полив водой
SOAP = 2  # полив мыльной пеной
BRUSH = 3  # чистка щётками


# взаимодействие с роботом вынесено в отдельную функцию
def transfer_to_cleaner(message):
    print(message)


# перемещение
def move(transfer, dist, state):
    angle_rads = state.angle * (math.pi / 180.0)
    new_state = RobotState(
        state.x + dist * math.cos(angle_rads),
        state.y + dist * math.sin(angle_rads),
        state.angle,
        state.state,
    )
    transfer(("POS(", new_state.x, ",", new_state.y, ")"))
    return new_state


# поворот
def turn(transfer, turn_angle, state):
    new_state = RobotState(
        state.x,
        state.y,
        state.angle + turn_angle,
        state.state,
    )
    transfer(("ANGLE", state.angle))
    return new_state


# установка режима работы
def set_state(transfer, new_internal_state, state):
    if new_internal_state == "water":
        self_state = WATER
    elif new_internal_state == "soap":
        self_state = SOAP
    elif new_internal_state == "brush":
        self_state = BRUSH
    else:
        return state
    new_state = RobotState(
        state.x,
        state.y,
        state.angle,
        self_state,
    )
    transfer(("STATE", self_state))
    return new_state


# начало чистки
def start(transfer, state):
    transfer(("START WITH", state.state))
    return state


# конец чистки
def stop(transfer, state):
    transfer(("STOP",))
    return state


# --- команды (Command) поверх того же домена ---


@dataclass(frozen=True, slots=True)
class Move:
    dist: int

    def execute(self, transfer, state):
        return move(transfer, self.dist, state)


@dataclass(frozen=True, slots=True)
class Turn:
    angle: int

    def execute(self, transfer, state):
        return turn(transfer, self.angle, state)


@dataclass(frozen=True, slots=True)
class SetMode:
    mode: str

    def execute(self, transfer, state):
        return set_state(transfer, self.mode, state)


@dataclass(frozen=True, slots=True)
class Start:
    def execute(self, transfer, state):
        return start(transfer, state)


@dataclass(frozen=True, slots=True)
class Stop:
    def execute(self, transfer, state):
        return stop(transfer, state)

