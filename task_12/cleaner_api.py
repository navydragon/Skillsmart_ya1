
# api получает на вход список команд и аргументов строкой
# стартовое состояние кладется на стек, после каждой операции возвращенное состояние снова кладется на стек
# _run_stream - парсит строку и выполняет команды - если пришла "не-команда", то она парсится как число или строка и кладется на стек
# если пришла команда, то она выполняется, если нужно, то берет из стека аргументы и результат кладет обратно на стек
# _parse_literal - парсит литералы из команды в числа или строки

# подход предполагает что с клиента придет правильная строка, иначе
# довольно сложно выглядит процесс обработки ошибок - придется проверять длину стека
# и типы "popped" значений для каждой операции по-своему

# реализовал ввод из консоли но тут постфиксная нотация будет явно смущать пользователя
# операция должна идти до аргумента, а тут аргументы идут до оператора

import pure_robot


def parse_literal(token):
    s = token.strip()
    if not s:
        return token
    # Режимы 
    if s in ("water", "soap", "brush"):
        return s
    # Целые
    signless = s[1:] if s[0] in "+-" else s
    if signless.isdigit():
        return int(s)
    # Float
    if "." in s:
        try:
            return float(s)
        except ValueError:
            return token
    return token


class RobotApi:

    def __init__(self, transfer=pure_robot.transfer_to_cleaner):
        self._transfer = transfer
        self.cleaner_state = pure_robot.RobotState(0.0, 0.0, 0.0, pure_robot.WATER)

    def run_stream(self, code, state):
        tokens = code.split()
        work_stack = [state]

        for tok in tokens:
            if tok == "move":
                dist = work_stack.pop()
                st = work_stack.pop()
                work_stack.append(pure_robot.move(self._transfer, dist, st))
            elif tok == "turn":
                turn_angle = work_stack.pop()
                st = work_stack.pop()
                work_stack.append(pure_robot.turn(self._transfer, turn_angle, st))
            elif tok == "set":
                mode = work_stack.pop()
                st = work_stack.pop()
                work_stack.append(pure_robot.set_state(self._transfer, mode, st))
            elif tok == "start":
                st = work_stack.pop()
                work_stack.append(pure_robot.start(self._transfer, st))
            elif tok == "stop":
                st = work_stack.pop()
                work_stack.append(pure_robot.stop(self._transfer, st))
            else:
                work_stack.append(parse_literal(tok))

        if not work_stack:
            return state
        return work_stack[-1]

    def make(self, code):
        self.cleaner_state = self.run_stream(code, self.cleaner_state)
        return self.cleaner_state

    def __call__(self, code):
        return self.make(code)


api = RobotApi()

