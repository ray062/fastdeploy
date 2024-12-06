# src/application/interfaces.py
from abc import ABC, abstractmethod
from pathlib import Path

class FileMonitor(ABC):
    @abstractmethod
    def start_monitoring(self, directory: Path) -> None:
        pass

    @abstractmethod
    def stop_monitoring(self) -> None:
        pass
