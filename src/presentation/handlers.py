# src/presentation/handlers.py
from pathlib import Path
import logging
from watchdog.events import FileSystemEventHandler
from ..application.use_cases import DeploymentUseCase
from ..domain.entities import Profile

_logger = logging.getLogger(__name__)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, profile: Profile, deployment_use_case: DeploymentUseCase):
        self.profile = profile
        self.deployment_use_case = deployment_use_case

    def on_modified(self, event):
        if event.is_directory:
            return

        if not self.profile.deployment.auto_deploy:
            response = input(f"Deploy {event.src_path} to remote server? ([y]/n): ")
            if response.lower() != 'y' and response != '':
                return

        self.deployment_use_case.deploy_file(self.profile, Path(event.src_path))

    def on_deleted(self, event):
        """Handle deletion of files/directories"""
        if event.is_directory:
            _logger.info(f"Directory deleted: {event.src_path}")
            _logger.warning(f"Deleting remote directory is not implemented yet")
            return  # Optionally handle directory deletions differently

        if not self.profile.deployment.auto_deploy:
            response = input(f"Delete {event.src_path} to remote server? ([y]/n): ")
            if response.lower() != 'y' and response != '':
                return
        try:
            # Delete the file on remote server
            self.deployment_use_case.delete_remote_file(str(event.src_path))
        except Exception as e:
            _logger.error(f"Failed to delete remote file {event.src_path}: {e}")