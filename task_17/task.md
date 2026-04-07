Stream Processing: нюансы

def main():
    event_store = EventStore()
    initial_state = RobotState(0.0, 0.0, 0, CleaningMode.WATER.value)
    state_projector = StateProjector(initial_state)
    
    command_handler = CommandHandler(event_store)
    
    movement_processor = MovementProcessor(event_store, state_projector)
    state_processor = StateProcessor(event_store, state_projector)
    logging_processor = LoggingProcessor(event_store, state_projector)
    
    robot_id = "robot_001"
    
    commands = [
        MoveCommand(100),
        TurnCommand(-90),
        SetStateCommand(CleaningMode.SOAP),
        StartCommand(),
        MoveCommand(50),
        StopCommand()
    ]
    
    for i, cmd in enumerate(commands):
        print(f"\n--- Cmd {i+1}: {cmd.get_command_type()} ---")
        command_handler.handle_command(robot_id, cmd)
        
        time.sleep(0.1)
        
        current_state = state_projector.project_state(robot_id, 
            event_store.get_events_for_robot(robot_id))
        print(f"State: {current_state}")
    
    print(f"\n=== All events ({len(event_store.get_all_events())}) ===")
    for i, event in enumerate(event_store.get_all_events()):
        print(f"{i+1}. {event.get_event_type()}")

...

--- Cmd 5: MOVE 50 ---
[MovementProcessor] Processing move request for robot robot_001
[LoggingProcessor] Event logged: ROBOT_MOVED from (100.0, 0.0) to (100.0, -50.0)
[LoggingProcessor] Event logged: MOVE_REQUESTED 50
State: RobotState(x=100.0, y=-50.0, angle=-90, state=2)

--- Cmd 6: STOP ---
[StateProcessor] Processing stop request for robot robot_001
[LoggingProcessor] Event logged: ROBOT_STOPPED
[LoggingProcessor] Event logged: STOP_REQUESTED
State: RobotState(x=100.0, y=-50.0, angle=-90, state=2)

=== All events (12) ===
1. MOVE_REQUESTED 100
2. ROBOT_MOVED from (0.0, 0.0) to (100.0, 0.0)
3. TURN_REQUESTED -90
4. ROBOT_TURNED from 0 to -90
5. STATE_CHANGE_REQUESTED SOAP
6. ROBOT_STATE_CHANGED from 1 to 2
7. START_REQUESTED
8. ROBOT_STARTED
9. MOVE_REQUESTED 50
10. ROBOT_MOVED from (100.0, 0.0) to (100.0, -50.0)
11. STOP_REQUESTED
12. ROBOT_STOPPED
Но тут есть очень важный нюанс.


class EventStore:
    def __init__(self):
        self._events: List[Event] = []
        self._subscribers: List[Callable[[Event], None]] = []
        self._lock = threading.RLock() <<<====
Что будет, если threading.RLock() заменить на threading.Lock() ?

Ваш ответ в свободной форме введите в форму ниже: