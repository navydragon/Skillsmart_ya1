from cleaner_api import api


if __name__ == "__main__":
    print("Введите конкатенативный сценарий (постфиксные токены), например:")
    print("  100 move -90 turn soap set start 50 move stop")
    print("Пустая строка или `exit` завершит ввод.")

    while True:
        line = input("> ").strip()
        if not line or line.lower() == "exit":
            break

        try:
            final_state = api(line)
            print("FINAL:", final_state)
        except Exception as e:
            # Ошибки распознавания кривого сценария/стека лучше показывать явно.
            print("ERROR:", type(e).__name__, str(e))

