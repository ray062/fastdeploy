# src/infrastructure/config/configuration.py
import os
import argparse
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AppConfig:
    profiles_path: Path
    logs_path: Path
    profile_name: str = None

class ConfigurationManager:
    @staticmethod
    def load_config() -> AppConfig:
        parser = argparse.ArgumentParser(description='File monitoring and deployment tool')
        parser.add_argument('--profile', help='Specify the profile to use')
        parser.add_argument('--profiles-path', help='Path to profiles directory')
        parser.add_argument('--logs-path', help='Path to logs directory')

        args = parser.parse_args()
        script_dir = Path(__file__).parent.parent.parent.parent

        return AppConfig(
            profiles_path=Path(args.profiles_path or os.getenv('DEPLOY_PROFILES_PATH', script_dir / 'profiles')),
            logs_path=Path(args.logs_path or os.getenv('DEPLOY_LOGS_PATH', script_dir / 'logs')),
            profile_name=args.profile
        )
