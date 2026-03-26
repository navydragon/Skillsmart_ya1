# Понял задачу так: нам нужно обернуть pure_robot в монаду состояний, чтобы можно было
# использовать его в цепочке вычислений. Для этого мы создаем класс RobotFlow, который
# содержит функцию run, которая принимает состояние и возвращает результат и новое состояние.
# bind/then сами прокидывают RobotState дальше, то есть применяют функцию к результату и передают новое состояние
# class RobotApi - для удобства клиента
# получается декларативный подход, когда мы описываем цепочку вычислений, есть state, который
# передается по цепочке, но не мутируется
# что очень понравилось - нет "прямого роутинга" if/elif и при этом все иммутабельно

# но если честно, то задачу "Реализуйте вариант с монадами состояний так, как вы это смогли понять :)"
# я не совсем выполнил, и часть кода я "подрезал".
# для разработчиков без ФП-бэкграунда (как я), которые не могут сходу запилить lambda
# монадная обертка выглядит громоздкой и некрасивой


import pure_robot


class RobotFlow:
    def __init__(self, runner):
        self._runner = runner

    def execute(self, state):
        return self._runner(state)

    def __rshift__(self, next_flow):
        def run_in_order(state):
            _, state_after_current = self.execute(state)
            return next_flow.execute(state_after_current)

        return RobotFlow(run_in_order)

    @staticmethod
    def start_with(value):
        # стартовый пустой шаг
        def keep_as_is(state):
            return value, state

        return RobotFlow(keep_as_is)


def _step(action):
    def run(state):
        return None, action(state)

    return RobotFlow(run)


def move_m(transfer, dist):
    def action(state):
        return pure_robot.move(transfer, dist, state)

    return _step(action)


def turn_m(transfer, angle):
    def action(state):
        return pure_robot.turn(transfer, angle, state)

    return _step(action)


def set_state_m(transfer, mode):
    def action(state):
        return pure_robot.set_state(transfer, mode, state)

    return _step(action)


def start_m(transfer):
    def action(state):
        return pure_robot.start(transfer, state)

    return _step(action)


def stop_m(transfer):
    def action(state):
        return pure_robot.stop(transfer, state)

    return _step(action)


class RobotApi:
    def __init__(self, transfer=pure_robot.transfer_to_cleaner):
        self._transfer = transfer
        self.cleaner_state = pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)

    def run_chain(self, chain):
        _, self.cleaner_state = chain.execute(self.cleaner_state)
        return self.cleaner_state

    def move(self, dist):
        return move_m(self._transfer, dist)

    def turn(self, angle):
        return turn_m(self._transfer, angle)

    def set_mode(self, mode):
        return set_state_m(self._transfer, mode)

    def start(self):
        return start_m(self._transfer)

    def stop(self):
        return stop_m(self._transfer)

