import paramiko


class AerpawSsh:
    client = None

    def __init__(self, hostname, username, keyfile):
        self.key = paramiko.RSAKey.from_private_key_file(keyfile)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=hostname, username=username, pkey=self.key, banner_timeout=200)

    def send_command(self, command, verbose: bool = False, mock: bool = False) -> (str, str):
        response = ''
        exit_code = 1
        if mock:
            return 'mock: {0}'.format(command), 0
        if self.client:
            try:
                stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
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
                response = exc
                exit_code = 1
                self.close()
        else:
            print("Connection not opened.")
        return response, exit_code

    def close(self):
        self.client.close()
