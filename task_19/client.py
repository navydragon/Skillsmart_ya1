
from ast_robot import (
    BRUSH,
    Move,
    MoveResponse,
    RobotState,
    SOAP,
    Start,
    Stop,
    SetState,
    Turn,
    WATER,
)


def build_demo_program():
    stop = Stop()
    after_move = SetState(BRUSH, lambda _: stop)
    work_block = Move(50, lambda _: after_move)
    cont = Start(work_block)

    on_ok = Turn(-90, lambda _: SetState(SOAP, lambda _: cont))


    on_barrier = SetState(SOAP, lambda _: Turn(-90, lambda _: cont))

    return Move(100, lambda r: on_ok if r == MoveResponse.OK else on_barrier)


if __name__ == "__main__":
    program = build_demo_program()
    initial = RobotState(0.0, 0.0, 0, WATER, 10, 10)
    final_state, log = program.interpret(initial, [])
    print(final_state)
    print(log)
