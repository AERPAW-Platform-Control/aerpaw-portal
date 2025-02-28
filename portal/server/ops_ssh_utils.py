import os
import paramiko
from portal.apps.error_handling.error_dashboard import new_error
from portal.apps.users.models import AerpawUser
PASSWORD = os.getenv('AERPAW_OPS_PORTAL_PASSWORD')

class AerpawSsh:
    client = None

    def __init__(self, hostname, username, keyfile):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.key = paramiko.RSAKey.from_private_key_file(keyfile)
            self.client.connect(hostname=hostname, username=username, pkey=self.key, banner_timeout=200)

            print(' Woohoo!! Connected!!')
            
        except paramiko.AuthenticationException as auth_exc:
            print("Authentication failed, please check your credentials.")
            new_error(auth_exc, user=AerpawUser.objects.get(username = username))
        except paramiko.SSHException as ssh_exception:
            print(f"SSH error: {ssh_exception}")
            new_error(ssh_exception, user=AerpawUser.objects.get(username = username))
        except Exception as exc:
            new_error(exc, user=AerpawUser.objects.get(username = username))



    def send_command(self, command, user: AerpawUser = None, verbose: bool = False, mock: bool = False, ) -> (str, str):
        print(f'sending command to control framework...')
        print(f'command= {command}')
        response = ''
        exit_code = 1
        """ if mock:
            return 'mock: {0}'.format(command), 0 """
        if self.client:
            try:
                full_command = f"echo {PASSWORD} | sudo -S {command}"
                stdin, stdout, stderr = self.client.exec_command(full_command, get_pty=True)
                if verbose:
                    response = bytes()
                    while not stdout.channel.exit_status_ready():
                        _out = stdout.channel.recv(1024)
                        response += _out
                        print(_out.decode("utf-8").strip("\n"))
                    response = response.decode("utf-8").strip("\n")
                else:
                    response = stdout.read().decode("utf-8").strip("\n")
                exit_code = stdout.channel.recv_exit_status()
                stdin.close()
                self.close()
            
            except Exception as exc:
                new_error(exc, user)
                response = exc
                exit_code = 1
                self.close()
        else:
            print("Connection not opened.")
        return response, exit_code
    
    def close(self):
        self.client.close()
