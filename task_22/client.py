from capabilities_robot import make_robot


def main():
    robot = make_robot()
    robot = (
        robot.move(100)
        .turn(-90)
        .set_soap()
        .start()
        .move(50)
        .move(50)
        .stop()
    )
    print(robot.log())


if __name__ == "__main__":
    main()

