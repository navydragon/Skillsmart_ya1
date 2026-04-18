from __future__ import annotations

from task_20.robot_adt import (
    BRUSH,
    SOAP,
    WATER,
    Move,
    SetMode,
    Start,
    Stop,
    Turn,
    angle,
    create,
    mode,
    position,
    run,
    set_mode,
)


if __name__ == "__main__":
    program = [
        Start(),
        Move(100),
        Turn(-90),
        SetMode("soap"),
        Move(50),
        SetMode("brush"),
        Stop(),
    ]

    r0 = create(x=0.0, y=0.0, angle_deg=0.0, mode=WATER)
    r1, log = run(program, r0)

    print("Start:", position(r0), angle(r0), mode(r0))
    r2 = set_mode(r1, "brush")
    print("Finish:  ", position(r2), angle(r2), mode(r2))
    print("Log:", log)

