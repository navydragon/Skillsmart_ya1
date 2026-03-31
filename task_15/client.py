from task_15.pure_robot import Move, SetMode, Start, Stop, Turn

from task_15.command_handler import CommandHandler
from task_15.events import EventStore, replay_events


def main():
    store = EventStore()
    handler = CommandHandler(store)

    robot_1 = "cleaner-1"
    robot_2 = "cleaner-2"

    # Клиент не держит состояние — только шлёт команды; состояние можно заново получить из журнала.
    handler.handle(robot_1, Move(10))
    handler.handle(robot_1, Turn(90))
    handler.handle(robot_1, SetMode("soap"))
    handler.handle(robot_1, Start())
    handler.handle(robot_1, Move(5))
    handler.handle(robot_1, Stop())

    handler.handle(robot_2, Move(1))
    handler.handle(robot_2, Turn(180))

    print("robot_1 state (replay):", replay_events(store.get_events(robot_1)))
    print("robot_2 state:", replay_events(store.get_events(robot_2)))


if __name__ == "__main__":
    main()
