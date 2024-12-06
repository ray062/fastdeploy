# src/domain/interfaces/repositories.py
from abc import ABC, abstractmethod
from typing import List
from ..entities import Profile

class ProfileRepository(ABC):
    @abstractmethod
    def get_profile(self, name: str) -> Profile:
        pass

    @abstractmethod
    def get_available_profiles(self) -> List[str]:
        pass