# src/application/use_cases.py
import logging
from typing import Protocol
from pathlib import Path
from ..domain.entities import Profile
from ..domain.interfaces.services import SSHService

__logger__ = logging.getLogger(__name__)

class DeploymentUseCase:
    def __init__(self, ssh_service: SSHService):
        self.ssh_service = ssh_service

    def calculate_remote_path(self, profile: Profile, local_path: Path) -> Path:
        # Calculate the relative path from the watch directory
        relative_path = local_path.relative_to(profile.deployment.watch_path)
        # Construct the remote path
        remote_path = Path(profile.deployment.remote_path) / relative_path
        return remote_path

    def deploy_file(self, profile: Profile, local_path: Path) -> None:
        # Execute pre-deploy commands
        if profile.commands.pre_deploy:           
            for cmd in profile.commands.pre_deploy:
                __logger__.debug(f"Executing Pre-deploy command: {cmd}")
                exit_code, output, error = self.ssh_service.execute_command(cmd)
                if exit_code != 0:
                    raise RuntimeError(f"Pre-deploy command failed: {error}")

        # Transfer file
        remote_path = self.calculate_remote_path(profile, local_path)
        __logger__.info(f"Transferring file {local_path} to remote server")
        self.ssh_service.transfer_file(local_path, remote_path)

        # Execute post-deploy commands
        if profile.commands.post_deploy:
            for cmd in profile.commands.post_deploy:
                __logger__.debug(f"Executing Post-deploy command: {cmd}")
                exit_code, output, error = self.ssh_service.execute_command(cmd)
                if exit_code != 0:
                    raise RuntimeError(f"Post-deploy command failed: {error}")
                
        __logger__.info(f"File {local_path} deployed successfully to remote server")
    

    def delete_remote_file(self, local_path: Path):
        remote_path = self.calculate_remote_path(local_path)
        """Delete a file on the remote server"""
        command = f"rm -f {remote_path}"
        __logger__.info(f"Delete remote file: {remote_path}")
        stdin, stdout, stderr = self.ssh_service.execute_command(command)
        
        # Check for errors
        error = stderr.strip()
        if error:
            raise Exception(f"Error deleting remote file: {error}")
        