# Как понял задачу - нужно взять идейную реализацию из примера и переписать ее так,
# чтобы инъекция была одной функцией. В примере есть класс RobotApi, который содержит
# make_apply_op подшивает transfer и возвращает и возвращает одну функцию apply_op, 
# внутри которой по имени команды вызываются те же pure_robot
# То есть, при вызове api("move 10") будет вызвана apply_op("move", ["10"], state)
# и в pure_robot будет передан transfer и state и команда
# Преимущество очевидно -  одна точка, которую можно подменить или настроить,
#  одна сигнатура в setup и один вызов в make, вместо пяти функций
# Да и внешне выглдяит стройнее и понятнее

from __future__ import annotations

from typing import Callable

import pure_robot

State = pure_robot.RobotState


def make_apply_op(
    transfer: Callable[[object], None],
) -> Callable[[str, list[str], State], State]:
    def apply_op(op: str, args: list[str], state: State) -> State:
        if op == "move":
            return pure_robot.move(transfer, int(args[0]), state)
        if op == "turn":
            return pure_robot.turn(transfer, int(args[0]), state)
        if op == "set":
            return pure_robot.set_state(transfer, args[0], state)
        if op == "start":
            return pure_robot.start(transfer, state)
        if op == "stop":
            return pure_robot.stop(transfer, state)
        return state

    return apply_op


class RobotApi:
    def setup(self, apply_op: Callable[[str, list[str], State], State]) -> None:
        self.apply_op = apply_op

    def make(self, command: str) -> State:
        if not hasattr(self, "cleaner_state"):
            self.cleaner_state = pure_robot.RobotState(
                0.0, 0.0, 0.0, pure_robot.WATER
            )
        cmd = command.split()
        if not cmd:
            return self.cleaner_state
        self.cleaner_state = self.apply_op(cmd[0], cmd[1:], self.cleaner_state)
        return self.cleaner_state

    def __call__(self, command: str) -> State:
        return self.make(command)


api = RobotApi()
api.setup(make_apply_op(pure_robot.transfer_to_cleaner))
