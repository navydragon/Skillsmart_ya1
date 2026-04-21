# Понял задачу так: нужно закрыть возможность выполнения недопустимых команд, при этом сохранив
# иммутабельность и состояние скрыто внутри замыкания. 

# Обертка RobotCaps не хранит RobotState, флаги и т.д. 
# Вместо этого он хранит только две функции (get_command, log_fn), которые являются замыканиями и помнят”состояние внутри build().
# Клиентскому коду это состояние недоступно как поля объекта.
# Каждая команда  при вызове возвращает новый RobotCaps, который создаётся внутри build() и содержит новое замыкание,
# помнящее обновлённые state/log/can_move. Доступность команд задаётся в get_command() через проверку allowed: 
# если команда недоступна, то, например, move не даёт реальное движение, а возвращает заглушку.

# В рамках обычного клиентского кода доступ к RobotState закрыт, клиент видит только RobotCaps и команды.
# Это обеспечивает защиту от "дурака", что круто, но не от злого хакера, т.к. абсолютной защиты в Python всё равно нет

import math
from collections import namedtuple

RobotState = namedtuple("RobotState", "x y angle mode water soap")

# режимы работы устройства очистки
WATER = 1  # полив водой
SOAP = 2  # полив мыльной пеной
BRUSH = 3  # чистка щётками


class MoveResponse:
    OK = "MOVE_OK"
    BARRIER = "HIT_BARRIER"


class SetModeResponse:
    OK = "MODE_OK"
    NO_WATER = "OUT_OF_WATER"
    NO_SOAP = "OUT_OF_SOAP"


def transfer_to_cleaner(message):
    print(message)


def _check_resources(state, new_mode):
    if new_mode == WATER and state.water <= 0:
        return SetModeResponse.NO_WATER
    if new_mode == SOAP and state.soap <= 0:
        return SetModeResponse.NO_SOAP
    return SetModeResponse.OK


def _check_position(*, x, y, x_min, x_max, y_min, y_max):
    constrained_x = max(x_min, min(x_max, x))
    constrained_y = max(y_min, min(y_max, y))
    if x == constrained_x and y == constrained_y:
        return constrained_x, constrained_y, MoveResponse.OK
    return constrained_x, constrained_y, MoveResponse.BARRIER


def step_emit(*, state, log, line, can_move):
    return state, log + (line,), can_move, (line,)


def step_turn(*, state, log, angle):
    new_state = RobotState(
        state.x,
        state.y,
        state.angle + angle,
        state.mode,
        state.water,
        state.soap,
    )
    line = f"ANGLE {new_state.angle}"
    return new_state, log + (line,), True, (line,)


def step_move(*, state, log, dist, x_min, x_max, y_min, y_max):
    angle_rads = state.angle * (math.pi / 180.0)
    raw_x = state.x + dist * math.cos(angle_rads)
    raw_y = state.y + dist * math.sin(angle_rads)
    cx, cy, resp = _check_position(
        x=raw_x,
        y=raw_y,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
    )
    new_state = RobotState(
        cx,
        cy,
        state.angle,
        state.mode,
        state.water,
        state.soap,
    )

    pos_line = f"POS({int(cx)},{int(cy)})"
    new_log = log + (pos_line,)
    emitted = (pos_line,)
    if resp == MoveResponse.BARRIER:
        new_log = new_log + (MoveResponse.BARRIER,)
        emitted = emitted + (MoveResponse.BARRIER,)
        return new_state, new_log, False, emitted

    return new_state, new_log, True, emitted


def step_set_mode(*, state, log, new_mode, can_move):
    resp = _check_resources(state, new_mode)
    if resp != SetModeResponse.OK:
        return state, log + (resp,), can_move, (resp,)

    new_state = RobotState(
        state.x,
        state.y,
        state.angle,
        new_mode,
        state.water,
        state.soap,
    )
    line = f"STATE {new_mode}"
    return new_state, log + (line,), can_move, (line,)


class RobotCaps:

    __slots__ = ("__get_command", "__log_fn")

    def __init__(self, get_command, log_fn):
        self.__get_command = get_command
        self.__log_fn = log_fn

    def __getattr__(self, name):
        return self.__get_command(name)

    def log(self):
        return self.__log_fn()


def make_robot(
    *,
    initial=None,
    transfer=None,
    x_min=0.0,
    x_max=100.0,
    y_min=0.0,
    y_max=100.0,
):
    """
    Фабрика capability-API.

    Важная идея: клиент никогда не видит RobotState напрямую и не может
    выполнить недопустимую команду, соответствующей функции просто не будет.
    """

    if initial is None:
        initial = RobotState(0.0, 0.0, 0, WATER, 10, 10)

    transfer_fn = transfer or transfer_to_cleaner

    def build(state, log, *, can_move):
        def log_fn():
            return log

        def apply_step(result):
            new_state, new_log, new_can_move, emitted = result
            for line in emitted:
                transfer_fn(line)
            return build(new_state, new_log, can_move=new_can_move)

        caps = None

        def missing(cmd_name):
            def _missing(*_args, **_kwargs):
                transfer_fn(f"ОШИБКА: команда '{cmd_name}' сейчас недоступна")
                return caps

            return _missing

        def get_command(name):
            allowed = {
                "turn": True,
                "set_brush": True,
                "start": True,
                "stop": True,
                "move": can_move,
                "set_water": state.water > 0,
                "set_soap": state.soap > 0,
            }

            if not allowed.get(name, False):
                return missing(name)

            def apply(result):
                return apply_step(result)

            handlers = {
                "move": lambda dist: apply(
                    step_move(
                        state=state,
                        log=log,
                        dist=dist,
                        x_min=x_min,
                        x_max=x_max,
                        y_min=y_min,
                        y_max=y_max,
                    )
                ),
                "turn": lambda angle: apply(
                    step_turn(
                        state=state,
                        log=log,
                        angle=angle,
                    )
                ),
                "set_water": lambda: apply(
                    step_set_mode(
                        state=state,
                        log=log,
                        new_mode=WATER,
                        can_move=can_move,
                    )
                ),
                "set_soap": lambda: apply(
                    step_set_mode(
                        state=state,
                        log=log,
                        new_mode=SOAP,
                        can_move=can_move,
                    )
                ),
                "set_brush": lambda: apply(
                    step_set_mode(
                        state=state,
                        log=log,
                        new_mode=BRUSH,
                        can_move=can_move,
                    )
                ),
                "start": lambda: apply(
                    step_emit(
                        state=state,
                        log=log,
                        line="START",
                        can_move=can_move,
                    )
                ),
                "stop": lambda: apply(
                    step_emit(
                        state=state,
                        log=log,
                        line="STOP",
                        can_move=can_move,
                    )
                ),
            }

            return handlers.get(name, missing(name))

        caps = RobotCaps(get_command, log_fn)
        return caps

    return build(initial, (), can_move=True)

