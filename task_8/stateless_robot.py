# Понял это задание так - нам нужно избежать хранения состояния робота
# в переменной, т.е. передавать это состояние в функцию и получать
# из нее новое значение. process_text_command получает state и команду
# и возвращает тоже state. run_program делает fold по списку команд
# Да, для теста достаточно подать state и команду и проверить результат
# Но, лишний слой :/ да и как взаимодействовать с "грязным миром"?
# Кажется, моя реализация "так себе"

from collections.abc import Iterable, Callable

from . import pure_robot


TransferFunc = Callable[[tuple], None]


def process_text_command(
    state: pure_robot.RobotState,
    command_str: str,
    transfer: TransferFunc | None = None,
) -> pure_robot.RobotState:


    transfer_func: TransferFunc = transfer or pure_robot.transfer_to_cleaner

    parts = command_str.split()
    if not parts:
        return state

    cmd, *args = parts

    if cmd == "move" and args:
        return pure_robot.move(transfer_func, int(args[0]), state)
    if cmd == "turn" and args:
        return pure_robot.turn(transfer_func, int(args[0]), state)
    if cmd == "set" and args:
        return pure_robot.set_state(transfer_func, args[0], state)
    if cmd == "start":
        return pure_robot.start(transfer_func, state)
    if cmd == "stop":
        return pure_robot.stop(transfer_func, state)

    return state


def run_program(
    commands: Iterable[str],
    initial_state: pure_robot.RobotState | None = None,
    transfer: TransferFunc | None = None,
) -> pure_robot.RobotState:

    state = initial_state or pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)
    for command in commands:
        state = process_text_command(state, command, transfer=transfer)
    return state


if __name__ == "__main__":
    program = [
        "move 100",
        "turn -90",
        "set soap",
        "start",
        "move 50",
        "stop",
    ]

    final_state = run_program(program)
    print("FINAL STATE:", final_state)

