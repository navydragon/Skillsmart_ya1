# Задача 21. Абстрактный тип данных
# a.k.a Лучшее из ООП и ФП
#
# Название урока уже дает подсказку куда смотреть, я по иттгу нашел концепцию Opaque ADT
# Как реализовано: - у нас есть старый добрый pure_robot.py, который мы используем как
# backend с чистыми функциями. Над ним м ы делает публичный фасад (ADT), который дает нам
# непрозрачный тип Robot и набор чистых функций. Robot - не настоящий класс, фактически там
# лежит экзампляр _RobotImpl, обертки, которая хранит состояние
# Но снаружи он вопринимается как Robot. Если список того, что считать публичным - (__all__ ),
# _wrap/_unwrap отвкечает за упаковку/распаковку - если кто-то передаст не тотт объект,
# то будет TypeError.
# у ADT есть геттеры вроде position(robot), angle(robot), mode(robot)
# операции move/turn/set_mode сами ничего не считают, а только
# дергают pure_robot, получают RobotState и упаковывают его обратно в opaque Robot
#
# Интересно, но реализация сложная и не очень понятная. Может быть есть более простой способ?


from collections import namedtuple
from typing import Any, NewType, cast

from task_20.pure_robot import BRUSH, SOAP, WATER, RobotState as _PureRobotState

_RobotState = namedtuple("_RobotState", "x y angle mode water soap")


class _RobotImpl:
    __slots__ = ("_state",)

    def __init__(self, state):
        self._state = state


Robot = NewType("Robot", object)

__all__ = [
    "BRUSH",
    "SOAP",
    "WATER",
    "Robot",
    "Move",
    "SetMode",
    "Start",
    "Stop",
    "Turn",
    "angle",
    "create",
    "mode",
    "move",
    "position",
    "run",
    "set_mode",
    "turn",
]


def _unwrap(robot):
    impl = cast(Any, robot)
    if not isinstance(impl, _RobotImpl):
        raise TypeError("Expected Robot created by create()")
    return impl


def _wrap(state):
    return cast(Robot, _RobotImpl(state))


def _to_pure_state(state):
    return _PureRobotState(state.x, state.y, state.angle, state.mode)


def _from_pure_state(pure_state):
    return _RobotState(
        float(pure_state.x),
        float(pure_state.y),
        float(pure_state.angle),
        int(pure_state.state),
        0.0,
        0.0,
    )


def _int_mode_to_str(mode_int):
    if mode_int == WATER:
        return "water"
    if mode_int == SOAP:
        return "soap"
    return "brush"


def create(*, x=0.0, y=0.0, angle_deg=0.0, mode=WATER):
    return _wrap(
        _RobotState(
            float(x),
            float(y),
            float(angle_deg),
            int(mode),
            0.0,
            0.0,
        )
    )


def position(robot):
    s = _unwrap(robot)._state
    return (s.x, s.y)


def angle(robot):
    return _unwrap(robot)._state.angle


def mode(robot):
    return _int_mode_to_str(_unwrap(robot)._state.mode)


def move(robot, distance):
    from task_20 import pure_robot as _backend

    s = _unwrap(robot)._state
    new_pure = _backend.move(lambda _msg: None, float(distance), _to_pure_state(s))
    return _wrap(_from_pure_state(new_pure))


def turn(robot, angle_deg):
    from task_20 import pure_robot as _backend

    s = _unwrap(robot)._state
    new_pure = _backend.turn(lambda _msg: None, float(angle_deg), _to_pure_state(s))
    return _wrap(_from_pure_state(new_pure))


def set_mode(robot, new_mode):
    from task_20 import pure_robot as _backend

    s = _unwrap(robot)._state
    new_pure = _backend.set_state(lambda _msg: None, new_mode, _to_pure_state(s))
    return _wrap(_from_pure_state(new_pure))


class Start:
    __slots__ = ()

    def execute(self, transfer, state):
        from task_20 import pure_robot as _backend

        return _backend.start(transfer, state)


class Stop:
    __slots__ = ()

    def execute(self, transfer, state):
        from task_20 import pure_robot as _backend

        return _backend.stop(transfer, state)


class Move:
    __slots__ = ("dist",)

    def __init__(self, dist):
        self.dist = dist

    def execute(self, transfer, state):
        from task_20 import pure_robot as _backend

        return _backend.move(transfer, self.dist, state)


class Turn:
    __slots__ = ("angle",)

    def __init__(self, angle):
        self.angle = angle

    def execute(self, transfer, state):
        from task_20 import pure_robot as _backend

        return _backend.turn(transfer, self.angle, state)


class SetMode:
    __slots__ = ("mode",)

    def __init__(self, mode):
        self.mode = mode

    def execute(self, transfer, state):
        from task_20 import pure_robot as _backend

        return _backend.set_state(transfer, self.mode, state)


def run(commands, robot):
    log = []

    def transfer(message):
        log.append(message)

    s = _unwrap(robot)._state
    state = _to_pure_state(s)
    for cmd in commands:
        state = cmd.execute(transfer, state)
    return _wrap(_from_pure_state(state)), log
