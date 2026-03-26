import cleaner_api


def main() -> None:
    api = cleaner_api.RobotApi()

    chain = (
        cleaner_api.RobotFlow.start_with(None)
        >> api.move(100)
        >> api.turn(-90)
        >> api.set_mode("soap")
        >> api.start()
        >> api.move(50)
        >> api.stop()
    )

    final_state = api.run_chain(chain)
    print("FINAL:", final_state)


if __name__ == "__main__":
    main()

