from task_16 import pure_robot
from task_16.events import (
    ModeSet,
    MoveRequestedEvent,
    RequestEvent,
    RobotMovedEvent,
    RobotTurnedEvent,
    SetModeRequestedEvent,
    StartRequestedEvent,
    Started,
    StopRequestedEvent,
    Stopped,
    TurnRequestedEvent,
    replay_events,
)


class EventProcessor:

    def __init__(self, store):
        self._store = store
        store.subscribe(self._on_event)

    def _is_cleaning_running(self, history):
        running = False
        for ev in history:
            if isinstance(ev, Started):
                running = True
            elif isinstance(ev, Stopped):
                running = False
        return running

    def _decide_results(self, event, history):
        current = replay_events(history)
        running = self._is_cleaning_running(history)

        if isinstance(event, MoveRequestedEvent):
            return [RobotMovedEvent(event.dist)]
        if isinstance(event, TurnRequestedEvent):
            return [] if event.angle == 0 else [RobotTurnedEvent(event.angle)]
        if isinstance(event, SetModeRequestedEvent):
            if running:
                raise ValueError("Нельзя менять режим во время активной чистки")
            if event.mode == "water" and current.state == pure_robot.WATER:
                return []
            return [ModeSet(event.mode)]
        if isinstance(event, StartRequestedEvent):
            if running:
                raise ValueError("Чистка уже запущена")
            return [Started()]
        if isinstance(event, StopRequestedEvent):
            if not running:
                raise ValueError("Нельзя остановить: чистка не запущена")
            return [Stopped()]
        return []

    def _on_event(self, robot_id, event):
        if not isinstance(event, RequestEvent):
            return
        history = self._store.get_events(robot_id)
        results = self._decide_results(event, history)
        if results:
            self._store.append_events(robot_id, results)
