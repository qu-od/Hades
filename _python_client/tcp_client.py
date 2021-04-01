from typing import List, Tuple, Dict, Optional
import socket

class Connection(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host: str
        self.port: int
        self.host, self.port = read_server_adress_from_file()
        self.is_refused = False
        try:
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            print('Connection refused. Server could be offline')
            self.is_refused = True
            return
        print(f'--- connected to the server {self.host}, port: {self.port}')

    '''def __del__(self):
        self.socket.close() #closing connection and then(?) using destructor
        print('Connection instance was destroyed. Connection closed')'''

    def send_message(self, message: bytes) -> Optional[bytes]:
        print(f'--- sending bytes message {message}...')
        self.socket.sendall(message)
        #ПОСТАВИТЬ ТАЙМАУТ 100МС
        server_response: bytes = self.socket.recv(1024)
        print('--- recieved data:', repr(server_response), '\n')
        return server_response

    def close(self):
        self.socket.close()
        print('--- Connection closed')

#------------------------functions---------------------------

def read_server_adress_from_file() -> Tuple[str, int]:
    server_name = 'default'
    # atm 'server_name' can be 'localhost' or 'worker' or 'default'
    with open('server_adress.txt', 'r') as F:
        for line in F: #reading adress from config file
            line_words = line.split(' ')
            if line_words[0] == server_name:
                HOST: str = line_words[1]
                PORT: int = int(line_words[2])
    # print(f'SERVER_NAME: {server_name}; HOST: {HOST}; PORT: {PORT}')
    return HOST, PORT

