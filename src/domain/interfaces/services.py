# src/domain/interfaces/services.py
from abc import ABC, abstractmethod
from pathlib import Path

class SSHService(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def execute_command(self, command: str) -> tuple[int, str, str]:
        pass

    @abstractmethod
    def transfer_file(self, local_path: Path, remote_path: Path) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
