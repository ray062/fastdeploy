# src/infrastructure/services/ssh_service.py
import logging
import os
import paramiko
from pathlib import Path
from ...domain.entities import SSHCredentials
from ...domain.interfaces.services import SSHService

_logger = logging.getLogger(__name__)

class ParamikoSSHService(SSHService):
    def __init__(self, credentials: SSHCredentials):
        self.credentials = credentials
        self.client = None
        self.sftp = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            # Load system host keys
            self.client.load_system_host_keys()
            # Optionally load from a custom known_hosts file
            self.client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
            # Keep using RejectPolicy for security
            self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
            
            # Now connect with the updated known_hosts
            connect_params = {
                'hostname': self.credentials.remote_host,
                'username': self.credentials.remote_user,
                'port': self.credentials.remote_port,
            }
            
            if self.credentials.auth_method == 'key':
                connect_params['pkey'] = self._load_private_key()
            else:
                connect_params['password'] = self.credentials.password

            self.client.connect(**connect_params)
            _logger.info(f"Connected to remote server: {self.credentials.remote_host}")
        except paramiko.ssh_exception.SSHException as e:
            if "not found in known_hosts" in str(e):
                helpful_message = f"""
    Server '{self.credentials.hostname}' not found in known_hosts.
    To resolve this, run the following command to verify and add the host key:

        ssh-keyscan -H {self.credentials.hostname} >> ~/.ssh/known_hosts

    Please verify the host key fingerprint before adding it to ensure security.
    """
                raise Exception(helpful_message) from e
            raise e
        except Exception as e:
            _logger.error(f"Failed to connect to remote server: {e}")
            raise e


    def _load_private_key(self) -> paramiko.PKey:
        key_path = os.path.expanduser(str(self.credentials.private_key_path))
        try:
            if self.credentials.private_key_passphrase:
                return paramiko.RSAKey.from_private_key_file(
                    key_path,
                    password=self.credentials.private_key_passphrase
                )
            return paramiko.RSAKey.from_private_key_file(key_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load private key: {e}")

    def execute_command(self, command: str) -> tuple[int, str, str]:
        assert self.client, "SSH client is not connected"
        stdin, stdout, stderr = self.client.exec_command(command)
        return (
            stdout.channel.recv_exit_status(),
            stdout.read().decode(),
            stderr.read().decode()
        )

    def transfer_file(self, local_path: Path, remote_path: Path) -> None:
        if not self.sftp:
            self.sftp = self.client.open_sftp()
        self.sftp.put(str(local_path), str(remote_path))

    def close(self) -> None:
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()