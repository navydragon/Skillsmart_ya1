from task_14.command_api import Batch, Move, SetMode, Start, Stop, Turn, api


def main():
    program = Batch(
        (
            Move(10),
            Turn(90),
            SetMode("soap"),
            Start(),
            Move(5),
            Stop(),
        )
    )
    final_state = api(program)
    print("FINAL:", final_state)


if __name__ == "__main__":
    main()

