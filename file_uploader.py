import argparse
import textwrap
import threading
import socket

class FileUploader:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print('FileUploader has been initialized...')
        print('args: ', self.args)
        print('buffer: ', self.buffer)
        print('socket: ', self.socket)
        print('\n')

    def run(self):
        if self.args.listen:
            self.listen()

        if self.args.upload:
            self.upload()

    def listen(self):
        self.socket.bind((self.args.target, int(self.args.port)))
        self.socket.listen(5)

        while True:
            client_socket, client_address = self.socket.accept()
            client_thread = threading.Thread(target=self.download, args=(client_socket,))
            client_thread.start()

    def upload(self):
        with open(f'{self.args.upload}', 'rb') as file:
            file_name = (self.args.upload + ' ').encode()
            data = file_name + file.read()

        self.socket.connect((self.args.target, int(self.args.port)))
        self.socket.send(data)
        self.terminate()

    @staticmethod
    def download(client_socket):
        buffer = b''

        while True:
            data = client_socket.recv(4000)

            if not data:
                break

            buffer += data

        buffer = buffer.split()
        file_name = buffer[0].decode()
        file_data = buffer[1:]

        with open(f'{file_name}', 'wb') as file:
            file_buffer = b''
            for data in file_data:
                file_buffer += data

            file.write(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='FileUploader',
        description='It uploads a file and download it on remote server',
        epilog=textwrap.dedent(f'''
        example:
        1. python ./file_uploader.py -t 191.18.5.194 -p 60000 -l
        2. python ./file_uploader.py -t 191.18.5.194 -p 60000 -u test_file.txt
        ''')
    )

    parser.add_argument('-t', '--target', help='Target IP')
    parser.add_argument('-p', '--port', help='Target Port')
    parser.add_argument('-l', '--listen', action='store_true', help='Listen')
    parser.add_argument('-u', '--upload', help='Upload a file')
    args = parser.parse_args()

    file_uploader = FileUploader(args)
    file_uploader.run()