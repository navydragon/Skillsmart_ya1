# Задание 10. Функциональная инъекция зависимостей (вариант: каждая зависимость отдельной функцией)
#
# Как понял задание: цель - отделить "сценарий" от “инъекции”:
# - сценарий (make_with_injected_deps) получает только нужные операции в виде функций и не знает ничего про transfer;
# - инъекция/сборка (bind_low_level) подшивает конкретный transfer в низкоуровневые функции
#   pure_robot и возвращает готовые зависимости-функции без параметра transfer
# make_with_injected_deps  не создает зависимости сам и не импортирует конкретный transfer. 
# Он просто "использует то, что дали"
# Что дает: можно подменять транспорт или отдельные функции, не меняя сценарный код и математику движения
# demo() показывает сборку системы


from __future__ import annotations

from functools import partial
from typing import Callable, Iterable, Sequence, TypeAlias

from . import pure_robot

State: TypeAlias = pure_robot.RobotState


def bind_low_level(
    transfer: Callable[[object], None],
) -> tuple[
    Callable[[int, State], State],
    Callable[[int, State], State],
    Callable[[str, State], State],
    Callable[[State], State],
    Callable[[State], State],
]:
    return (
        partial(pure_robot.move, transfer),
        partial(pure_robot.turn, transfer),
        partial(pure_robot.set_state, transfer),
        partial(pure_robot.start, transfer),
        partial(pure_robot.stop, transfer),
    )


def make_with_injected_deps(
    *,
    move_fn: Callable[[int, State], State],
    turn_fn: Callable[[int, State], State],
    set_state_fn: Callable[[str, State], State],
    start_fn: Callable[[State], State],
    stop_fn: Callable[[State], State],
    code: Sequence[str] | Iterable[str],
    state: State,
) -> State:

    for line in code:
        parts = line.split()
        if not parts:
            continue

        op = parts[0]
        if op == "move":
            state = move_fn(int(parts[1]), state)
        elif op == "turn":
            state = turn_fn(int(parts[1]), state)
        elif op == "set":
            state = set_state_fn(parts[1], state)
        elif op == "start":
            state = start_fn(state)
        elif op == "stop":
            state = stop_fn(state)
    return state


def demo() -> pure_robot.RobotState:

    transfer = pure_robot.transfer_to_cleaner
    move_fn, turn_fn, set_state_fn, start_fn, stop_fn = bind_low_level(transfer)

    start_state = pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)
    code = [
        "set soap",
        "start",
        "move 10",
        "turn 90",
        "move 5",
        "stop",
    ]

    return make_with_injected_deps(
        move_fn=move_fn,
        turn_fn=turn_fn,
        set_state_fn=set_state_fn,
        start_fn=start_fn,
        stop_fn=stop_fn,
        code=code,
        state=start_state,
    )


if __name__ == "__main__":
    final_state = demo()
    print("FINAL:", final_state)
