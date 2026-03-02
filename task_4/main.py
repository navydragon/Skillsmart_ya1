# Т.к. добрая часть моего кода находится внутри архитектуры MVC, то и здесь сразу выделил:
# model - сам робот и его чистые методы
# logger - модуль логирования с чистыми методами
# controller - модуль, который этим управляет,  оставляя методы выше чистыми
# programs - добавил возможность читать команлы из файла



from programs import load_program
from robot_controller import RobotController
from robot_logging import RobotLogger
from robot_model import Robot


def main() -> None:
    logger = RobotLogger()
    robot = Robot()
    controller = RobotController(robot, logger=logger)

    program = load_program("input.txt")
    controller.run_program(program)


if __name__ == "__main__":
    main()

