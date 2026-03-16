# Задание на DI. Как было понятоо: надо взять "хипстерскую архитектуру (исходно - файлы с префиксом initial_)" 
# и разделить интерфейс и реализацию, используя паттерн DI.
# Основной “контракт” для клиента - это интерфейс CleanerApiInterface, который определяет 
# методы для управления роботом. ClientCleanerApi реализует этот интерфейс, инкапсулируя 
# доменн pure_robot и способ общения с внешним миром TransferInterface.
# Клиент (initial_client.py) работает только с ClientCleanerApi и,
# при необходимости, может передать свою реализацию транспорта, не тровая домен.

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Protocol, runtime_checkable

import pure_robot


@runtime_checkable
class TransferInterface(Protocol):

    def send(self, message: object) -> None:
        pass


class PrintTransfer(TransferInterface):

    def send(self, message: object) -> None:
        print(message)


class CleanerApiInterface(ABC):
    """Интерфейс высокого уровня для управления роботом‑очистителем."""

    @abstractmethod
    def activate_cleaner(self, code: Iterable[str]) -> None:
        """Интерпретировать и выполнить последовательность текстовых команд."""

    @abstractmethod
    def get_x(self) -> float:
        """Текущая координата X робота."""

    @abstractmethod
    def get_y(self) -> float:
        """Текущая координата Y робота."""

    @abstractmethod
    def get_angle(self) -> float:
        """Текущий угол поворота робота в градусах."""

    @abstractmethod
    def get_state(self) -> int:
        """Текущее внутреннее состояние системы очистки."""


class ClientCleanerApi(CleanerApiInterface):

    def __init__(self, transfer: TransferInterface | None = None) -> None:
        # Транспорт можно заменить снаружи (dependency injection),
        # по умолчанию используется консольный вариант.
        self._transfer: TransferInterface = transfer or PrintTransfer()
        # Состояние робота живёт здесь, доменный слой ничего не знает о клиенте.
        self._state: pure_robot.RobotState = pure_robot.RobotState(
            0.0, 0.0, 0, pure_robot.WATER
        )

    def _transfer_to_cleaner(self, message: object) -> None:
        self._transfer.send(message)

    def activate_cleaner(self, code: Iterable[str]) -> None:
        self._state = pure_robot.make(self._transfer_to_cleaner, code, self._state)

    def get_x(self) -> float:
        return self._state.x

    def get_y(self) -> float:
        return self._state.y

    def get_angle(self) -> float:
        return self._state.angle

    def get_state(self) -> int:
        return self._state.state

