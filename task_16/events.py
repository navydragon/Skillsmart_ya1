from dataclasses import dataclass

from task_16 import pure_robot

_NOOP_TRANSFER = lambda _message: None


class RequestEvent:
    pass


class ResultEvent:
    pass


# запросы


@dataclass(frozen=True, slots=True)
class MoveRequestedEvent(RequestEvent):
    dist: int


@dataclass(frozen=True, slots=True)
class TurnRequestedEvent(RequestEvent):
    angle: int


@dataclass(frozen=True, slots=True)
class SetModeRequestedEvent(RequestEvent):
    mode: str


@dataclass(frozen=True, slots=True)
class StartRequestedEvent(RequestEvent):
    pass


@dataclass(frozen=True, slots=True)
class StopRequestedEvent(RequestEvent):
    pass


# результаты


@dataclass(frozen=True, slots=True)
class RobotMovedEvent(ResultEvent):
    dist: int


@dataclass(frozen=True, slots=True)
class RobotTurnedEvent(ResultEvent):
    angle: int


@dataclass(frozen=True, slots=True)
class ModeSet(ResultEvent):
    mode: str


@dataclass(frozen=True, slots=True)
class Started(ResultEvent):
    pass


@dataclass(frozen=True, slots=True)
class Stopped(ResultEvent):
    pass


def initial_state():
    return pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)


def apply_event(state, event):
    if isinstance(event, RobotMovedEvent):
        return pure_robot.move(_NOOP_TRANSFER, event.dist, state)
    if isinstance(event, RobotTurnedEvent):
        return pure_robot.turn(_NOOP_TRANSFER, event.angle, state)
    if isinstance(event, ModeSet):
        return pure_robot.set_state(_NOOP_TRANSFER, event.mode, state)
    if isinstance(event, Started):
        return pure_robot.start(_NOOP_TRANSFER, state)
    if isinstance(event, Stopped):
        return pure_robot.stop(_NOOP_TRANSFER, state)
    raise TypeError(f"Неизвестное событие для replay: {event!r}")


def replay_events(events):
    state = initial_state()
    for event in events:
        if not isinstance(event, ResultEvent):
            continue
        state = apply_event(state, event)
    return state


class EventStore:

    def __init__(self):
        self._streams = {}
        self._subscribers = []

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def get_events(self, robot_id):
        return tuple(self._streams.get(robot_id, ()))

    def append_events(self, robot_id, events):
        if not events:
            return
        if robot_id not in self._streams:
            self._streams[robot_id] = []
        stream = self._streams[robot_id]
        for ev in events:
            stream.append(ev)
            try:
                for cb in list(self._subscribers):
                    cb(robot_id, ev)
            except Exception:
                stream.pop()
                raise
