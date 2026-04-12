# AST-интерпретатор

# Строим дерево узлов с interpret() и next(response). в _next - отложенный вызов функции
# Другой обход (другой interpret) можно добавить, не меняя структуру узлов по сути, что прикольно.

# Не придумал, как по-человечески описывать последовательность команда "не с хвоста"
# (и при этом без вложенных lambda). А если к нам с консоли приходят команды -
# при этом логика интерпретации команд может быть сложной, как это реализовать 
# не замусорив код?

# В моей личном рейтинге "приятных архитектурных решений" этот вариант не очень высоко)))



from collections import namedtuple
import math

RobotState = namedtuple("RobotState", "x y angle state water soap")

WATER = 1
SOAP = 2
BRUSH = 3


class MoveResponse:
    OK = "MOVE_OK"
    BARRIER = "HIT_BARRIER"


class TurnResponse:
    OK = "TURN_OK"


class SetStateResponse:
    OK = "STATE_OK"
    NO_WATER = "OUT_OF_WATER"
    NO_SOAP = "OUT_OF_SOAP"


def check_position(x, y):
    constrained_x = max(0, min(100, x))
    constrained_y = max(0, min(100, y))

    if x == constrained_x and y == constrained_y:
        return (x, y, MoveResponse.OK)
    return (constrained_x, constrained_y, MoveResponse.BARRIER)


def check_resources(old_state, new_mode):
    if new_mode == WATER:
        if old_state.water <= 0:
            return SetStateResponse.NO_WATER
    elif new_mode == SOAP:
        if old_state.soap <= 0:
            return SetStateResponse.NO_SOAP
    return SetStateResponse.OK


class Stop:
    def interpret(self, state, log):
        return state, log + ["STOP"]


class Start:
    def __init__(self, next_node):
        self._next = next_node

    def interpret(self, state, log):
        return self._next.interpret(state, log + ["START"])


class Move:
    def __init__(self, distance, next_fn):
        self.distance = distance
        self._next = next_fn

    def interpret(self, state, log):
        angle_rads = state.angle * (math.pi / 180.0)
        raw_x = state.x + self.distance * math.cos(angle_rads)
        raw_y = state.y + self.distance * math.sin(angle_rads)
        cx, cy, resp = check_position(raw_x, raw_y)
        new_state = RobotState(
            cx,
            cy,
            state.angle,
            state.state,
            state.water,
            state.soap,
        )
        new_log = log + [f"POS({int(cx)},{int(cy)})"]
        if resp == MoveResponse.BARRIER:
            new_log = new_log + [MoveResponse.BARRIER]
        return self._next(resp).interpret(new_state, new_log)


class Turn:
    def __init__(self, angle, next_fn):
        self.angle = angle
        self._next = next_fn

    def interpret(self, state, log):
        new_state = RobotState(
            state.x,
            state.y,
            state.angle + self.angle,
            state.state,
            state.water,
            state.soap,
        )
        new_log = log + [f"ANGLE {new_state.angle}"]
        return self._next(TurnResponse.OK).interpret(new_state, new_log)


class SetState:
    def __init__(self, new_mode, next_fn):
        self.new_mode = new_mode
        self._next = next_fn

    def interpret(self, state, log):
        resp = check_resources(state, self.new_mode)
        if resp != SetStateResponse.OK:
            new_state = RobotState(
                state.x,
                state.y,
                state.angle,
                state.state,
                state.water,
                state.soap,
            )
            new_log = log + [resp]
        else:
            new_state = RobotState(
                state.x,
                state.y,
                state.angle,
                self.new_mode,
                state.water,
                state.soap,
            )
            new_log = log + [f"STATE {self.new_mode}"]
        return self._next(resp).interpret(new_state, new_log)
