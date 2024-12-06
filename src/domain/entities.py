
from dataclasses import dataclass
from typing import Optional, List, Dict
from pathlib import Path

@dataclass
class SSHCredentials:
    remote_host: str
    remote_user: str
    remote_port: int
    auth_method: str
    password: Optional[str] = None
    private_key_path: Optional[Path] = None
    private_key_passphrase: Optional[str] = None

@dataclass
class DeploymentConfig:
    watch_path: Path
    remote_path: Path
    auto_deploy: bool

    def __post_init__(self):
        self.watch_path = Path(self.watch_path)
        self.remote_path = Path(self.remote_path)

@dataclass
class Commands:
    pre_deploy: List[str]
    post_deploy: List[str]

@dataclass
class Profile:
    name: str
    credentials: SSHCredentials
    deployment: DeploymentConfig
    commands: Commands



