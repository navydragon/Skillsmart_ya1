# Расширение монадного робота:
# - check_position - координаты в [0, 100], иначе усечение и HIT_BARRIER.
# - check_resources(old_state, new_mode) - при переходе в WATER/SOAP проверка
#   счётчиков water и soap в состоянии; при отказе режим не меняется.
# - RobotState расширен полями water и soap; move/turn/set_state их сохраняют.
# Определенная проблема в том, что приходится тащить все новые поля state в каждый метод

from collections import namedtuple
import math

RobotState = namedtuple("RobotState", "x y angle state water soap")


WATER = 1
SOAP = 2
BRUSH = 3


class MoveResponse:
    OK = "MOVE_OK"
    BARRIER = "HIT_BARRIER"


class SetStateResponse:
    OK = "STATE_OK"
    NO_WATER = "OUT_OF_WATER"
    NO_SOAP = "OUT_OF_SOAP"


def check_position(x: float, y: float) -> tuple[float, float, str]:
    constrained_x = max(0, min(100, x))
    constrained_y = max(0, min(100, y))

    if x == constrained_x and y == constrained_y:
        return (x, y, MoveResponse.OK)
    return (constrained_x, constrained_y, MoveResponse.BARRIER)


def check_resources(old_state, new_mode: int) -> str:
    if new_mode == WATER:
        if old_state.water <= 0:
            return SetStateResponse.NO_WATER
    elif new_mode == SOAP:
        if old_state.soap <= 0:
            return SetStateResponse.NO_SOAP
    return SetStateResponse.OK


class StateMonad:
    def __init__(self, state, log=None):
        self.state = state
        self.log = log or []

    def bind(self, func):
        new_state, new_log = func(self.state, self.log)
        return StateMonad(new_state, new_log)


def move(dist):
    def inner(old_state, log):
        angle_rads = old_state.angle * (math.pi / 180.0)
        raw_x = old_state.x + dist * math.cos(angle_rads)
        raw_y = old_state.y + dist * math.sin(angle_rads)
        cx, cy, resp = check_position(raw_x, raw_y)
        new_state = RobotState(
            cx,
            cy,
            old_state.angle,
            old_state.state,
            old_state.water,
            old_state.soap,
        )
        new_log = log + [f"POS({int(cx)},{int(cy)})"]
        if resp == MoveResponse.BARRIER:
            new_log = new_log + [MoveResponse.BARRIER]
        return new_state, new_log

    return inner


def turn(angle):
    def inner(old_state, log):
        new_state = RobotState(
            old_state.x,
            old_state.y,
            old_state.angle + angle,
            old_state.state,
            old_state.water,
            old_state.soap,
        )
        return new_state, log + [f"ANGLE {new_state.angle}"]

    return inner


def set_state(new_mode):
    def inner(old_state, log):
        resp = check_resources(old_state, new_mode)
        if resp != SetStateResponse.OK:
            return (
                RobotState(
                    old_state.x,
                    old_state.y,
                    old_state.angle,
                    old_state.state,
                    old_state.water,
                    old_state.soap,
                ),
                log + [resp],
            )
        new_state = RobotState(
            old_state.x,
            old_state.y,
            old_state.angle,
            new_mode,
            old_state.water,
            old_state.soap,
        )
        return new_state, log + [f"STATE {new_mode}"]

    return inner


def start(old_state, log):
    return old_state, log + ["START"]


def stop(old_state, log):
    return old_state, log + ["STOP"]


if __name__ == "__main__":
    initial_state = StateMonad(RobotState(0.0, 0.0, 0, WATER, 10, 10))
    result = (
        initial_state.bind(move(100))
        .bind(turn(-90))
        .bind(set_state(SOAP))
        .bind(start)
        .bind(move(50))
        .bind(stop)
    )

