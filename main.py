# main.py
import logging
from pathlib import Path
import time

from watchdog.observers import Observer

from src.infrastructure.config.configuration import ConfigurationManager
from src.infrastructure.repositories.profile_repository import YAMLProfileRepository
from src.infrastructure.services.ssh_service import ParamikoSSHService
from src.application.use_cases import DeploymentUseCase
from src.presentation.handlers import FileChangeHandler
from src.presentation.cli import select_profile

def setup_logging(config, profile_name: str) -> None:
    config.logs_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(config.logs_path / f"{profile_name}.log"),
            logging.StreamHandler()
        ]
    )

def main():
    try:
        # Load configuration
        config = ConfigurationManager.load_config()
        
        # Initialize repositories
        profile_repo = YAMLProfileRepository(config.profiles_path)
        
        # Get available profiles
        available_profiles = profile_repo.get_available_profiles()
        if not available_profiles:
            raise ValueError(f"No profiles found in: {config.profiles_path}")

        # Select profile
        profile_name = config.profile_name
        if profile_name not in available_profiles:
            profile_name = select_profile(available_profiles)

        # Setup logging
        setup_logging(config, profile_name)

        # Load profile
        profile = profile_repo.get_profile(profile_name)
        
        # Initialize services and use cases
        ssh_service = ParamikoSSHService(profile.credentials)
        ssh_service.connect()
        
        deployment_use_case = DeploymentUseCase(ssh_service)
        
        # Create and start file system observer
        event_handler = FileChangeHandler(profile, deployment_use_case)
        observer = Observer()
        observer.schedule(
            event_handler,
            str(profile.deployment.watch_path),
            recursive=True
        )
        observer.start()

        logging.info(f"Using profile: {profile_name}")
        logging.info(f"Monitoring directory: {profile.deployment.watch_path}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            ssh_service.close()
            logging.info("Monitoring stopped")

        observer.join()

    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    main()
