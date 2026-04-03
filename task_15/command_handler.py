# Event Sourcing
#
# Как понял: состояние робота НЕ хранится между вызовами.
# Единственное мутабельное место - EventStore
# В store лежит журнал событий по robot_id: Moved/Turned/ModeSet/Started/Stopped.

# Как работает обработка команды:
# Клиент вызывает handler.handle(robot_id, command)
# CommandHandler читает из store все события этого robot_id (prior)
# CommandHandler пересобирает текущее состояние "с нуля" через replay_events(prior)
# (replay не печатает ничего в консоль)
# По команде (Move/Turn/SetMode/Start/Stop) вычисляется список новых событий new_events
#  Это не выполнение робота напрямую, а фиксация факта "что произошло"
#  new_events дописываются в store (append_events)
# Итоговое состояние снова получается только из store

# Очень интересный концепт, особенно если нужно откатить состояние назад!

# Но если у нас миллионы событий с тяжелыми вычислениями, то непонятно что делать

from task_15 import pure_robot
from task_15.pure_robot import Move, SetMode, Start, Stop, Turn

from task_15.events import (
    ModeSet,
    Moved,
    Started,
    Stopped,
    Turned,
    apply_event,
    replay_events,
)


class CommandHandler:

    def __init__(self, store):
        self._store = store

    def _is_cleaning_running(self, history):

        running = False
        for ev in history:
            if isinstance(ev, Started):
                running = True
            elif isinstance(ev, Stopped):
                running = False
        return running

    def _decide_new_events(self, command, history, current_state):

        running = self._is_cleaning_running(history)

        if isinstance(command, Move):
            dist = command.dist
            if dist < 0:
                raise ValueError("Нельзя двигаться на отрицательную дистанцию")
            return [Moved(dist)]

        if isinstance(command, Turn):
            angle = command.angle
            if angle == 0:
                return []
            if abs(angle) > 3600:
                raise ValueError("Слишком большой угол поворота")
            return [Turned(angle)]

        if isinstance(command, SetMode):
            mode = command.mode
            if mode not in ("water", "soap", "brush"):
                raise ValueError(f"Неизвестный режим: {mode!r}")
            if running:
                raise ValueError("Нельзя менять режим во время активной чистки")
            if mode == "water" and current_state.state == pure_robot.WATER:
                return []
            return [ModeSet(mode)]

        if isinstance(command, Start):
            if running:
                raise ValueError("Чистка уже запущена")
            return [Started()]

        if isinstance(command, Stop):
            if not running:
                raise ValueError("Нельзя остановить: чистка не запущена")
            return [Stopped()]

        raise TypeError(f"Неизвестная команда: {command!r}")

    def handle(self, robot_id, command):
        history = self._store.get_events(robot_id)
        current = replay_events(history)
        new_events = self._decide_new_events(command, history, current)


        self._store.append_events(robot_id, new_events)

        new_history = self._store.get_events(robot_id)
        final_state = replay_events(new_history)
        return final_state, tuple(new_events)
