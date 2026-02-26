# Я понял это задание так: 
# Взять представленный спегетти-код и преобразовать его архитектуру согласно процедурному подходу (подход "Программирование без GoTo"
# из курса Programming in small а именно:
# 1) Большая проблема делится на процедуры
# 2) У процедур общее состояние в виде глобальных переменных
# 3) Процедуры ничего не возвращают, но меняют глобальное состояние


import math

WATER = 1  # полив водой
SOAP = 2   # полив мыльной пеной
BRUSH = 3  # чистка метлой


robot: dict[str, float | int] = {
    "x": 0.0,
    "y": 0.0,
    "angle": 0.0,
    "state": WATER,
}


def init_robot() -> None:
    global robot
    robot["x"] = 0.0
    robot["y"] = 0.0
    robot["angle"] = 0.0
    robot["state"] = WATER


def do_move(dist: float) -> None:
    global robot
    angle_rads = robot["angle"] * (math.pi / 180.0)
    robot["x"] += dist * math.cos(angle_rads)
    robot["y"] += dist * math.sin(angle_rads)
    print("POS(", robot["x"], ",", robot["y"], ")")


def do_turn(delta: int) -> None:
    global robot
    robot["angle"] += delta
    print("ANGLE", robot["angle"])


def do_set(mode_name: str) -> None:
    global robot
    if mode_name == "water":
        robot["state"] = WATER
    elif mode_name == "soap":
        robot["state"] = SOAP
    elif mode_name == "brush":
        robot["state"] = BRUSH
    else:
        print("ОШИБКА неизвестный режим:", mode_name)
        return
    print("STATE", robot["state"])


def do_start() -> None:
    print("START WITH", robot["state"])


def do_stop() -> None:
    print("STOP")


def execute_command(command: str) -> None:
    cmd = command.split()
    if not cmd:
        return

    try:
        if cmd[0] == "move":
            do_move(int(cmd[1]))
        elif cmd[0] == "turn":
            do_turn(int(cmd[1]))
        elif cmd[0] == "set":
            do_set(cmd[1].lower())
        elif cmd[0] == "start":
            do_start()
        elif cmd[0] == "stop":
            do_stop()
        else:
            print("ОШИБКА неизвестная команда:", cmd[0])
    except (IndexError, ValueError) as e:
        print("ОШИБКА", e)


def run_program(code: list[str]) -> None:

    init_robot()
    for command in code:
        execute_command(command)


if __name__ == "__main__":
    program = [
        "move 100",
        "turn -90",
        "set soap",
        "start",
        "move 50",
        "stop",
    ]
    run_program(program)
