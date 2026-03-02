class RobotLogger:
    def log_position(self, x: float, y: float) -> None:
        print("POS(", x, ",", y, ")")

    def log_angle(self, angle: float) -> None:
        print("ANGLE", angle)

    def log_state(self, state: int) -> None:
        print("STATE", state)

    def log_start(self, mode: int) -> None:
        print("START WITH", mode)

    def log_stop(self) -> None:
        print("STOP")

    def log_unknown_mode(self, mode_name: str) -> None:
        print("ОШИБКА неизвестный режим:", mode_name)

    def log_unknown_command(self, cmd: str) -> None:
        print("ОШИБКА неизвестная команда:", cmd)

    def log_error(self, error: Exception) -> None:
        print("ОШИБКА", error)

