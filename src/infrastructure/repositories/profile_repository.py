# src/infrastructure/repositories/profile_repository.py
import yaml
from pathlib import Path
from typing import List
from ...domain.entities import Profile, SSHCredentials, DeploymentConfig, Commands
from ...domain.interfaces.repositories import ProfileRepository

class YAMLProfileRepository(ProfileRepository):
    def __init__(self, profiles_path: Path):
        self.profiles_path = profiles_path

    def get_profile(self, name: str) -> Profile:
        profile_path = self.profiles_path / f"{name}.yaml"
        with open(profile_path) as f:
            data = yaml.safe_load(f)
            
        return Profile(
            name=data['name'],
            credentials=SSHCredentials(**data['credentials']),
            deployment=DeploymentConfig(**data['deployment']),
            commands=Commands(**data['commands'])
        )

    def get_available_profiles(self) -> List[str]:
        return [f.stem for f in self.profiles_path.glob("*.yaml")]
