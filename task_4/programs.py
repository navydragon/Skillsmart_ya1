from pathlib import Path


def load_program(filename: str) -> list[str]:
    program_path = Path(__file__).with_name(filename)
    with program_path.open(encoding="utf-8") as source:
        return [line.strip() for line in source if line.strip()]

