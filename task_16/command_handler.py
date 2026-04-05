# Stream Processing 
#
# Клиент -  шлёт команды в CommandHandler, при необходимости смотрит снимок через 
#  replay_events(store.get_events(robot_id)).
#
# CommandHandler - только проверка команды и перевод в request-события.
# Бизнес-логика здесь не решается
#
# EventStore - журнал событий по robot_id. После каждой записи зовёт подписчиков.
# Если подписчик падает с ошибкой, последнее событие из потока убирается 
#
# EventProcessor - Подписан на store. На request-событиях читает историю и replay_events — учитываются только result-события.
# Решает: дописать result в store, не писать ничего или кинуть ValueError.
# Бизнес-логика должна быть тут

# events.py
# Request - намерение из команды, в проекцию состояния не входят.
# Result -  то, что replay_events накатывает через pure_robot (движение, режим, старт/стоп).
#
# Выглядит непхоло, но запутанно. Хотя каждая задача и отделена в свой файл.
# Пока что, несмотря на множественное упоминание в курсе, я не думаю в 
# первую очередь о мутабельности 

from task_16.pure_robot import Move, SetMode, Start, Stop, Turn

from task_16.events import (
    MoveRequestedEvent,
    SetModeRequestedEvent,
    StartRequestedEvent,
    StopRequestedEvent,
    TurnRequestedEvent,
    replay_events,
)


def _requests_for_move(command: Move):
    if command.dist < 0:
        raise ValueError("Нельзя двигаться на отрицательную дистанцию")
    return [MoveRequestedEvent(command.dist)]


def _requests_for_turn(command: Turn):
    if abs(command.angle) > 3600:
        raise ValueError("Слишком большой угол поворота")
    return [TurnRequestedEvent(command.angle)]


def _requests_for_set_mode(command: SetMode):
    if command.mode not in ("water", "soap", "brush"):
        raise ValueError(f"Неизвестный режим: {command.mode!r}")
    return [SetModeRequestedEvent(command.mode)]


def _requests_for_start(_command: Start):
    return [StartRequestedEvent()]


def _requests_for_stop(_command: Stop):
    return [StopRequestedEvent()]


_HANDLERS = {
    Move: _requests_for_move,
    Turn: _requests_for_turn,
    SetMode: _requests_for_set_mode,
    Start: _requests_for_start,
    Stop: _requests_for_stop,
}


class CommandHandler:

    def __init__(self, store):
        self._store = store

    def _requests_for_command(self, command):
        fn = _HANDLERS.get(type(command))
        if fn is None:
            raise TypeError(f"Неизвестная команда: {command!r}")
        return fn(command)

    def handle(self, robot_id, command):
        new_requests = self._requests_for_command(command)
        self._store.append_events(robot_id, new_requests)

        final_state = replay_events(self._store.get_events(robot_id))
        return final_state, tuple(new_requests)
