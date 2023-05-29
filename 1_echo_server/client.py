import socket
from socket_extension import ExtendedSocket


class EchoClient:

    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        # Создаем сокет
        self.client_socket = ExtendedSocket(socket.AF_INET, socket.SOCK_STREAM)
        # Подключаемся к серверу
        self.client_socket.connect((self.host, self.port))
        print(f"Подключение к серверу {self.host}:{self.port}")

    def send_receive(self, message):
        # Отправляем данные на сервер
        self.client_socket.send_text(message)
        print("Данные отправлены серверу.")
        # Receive data from server
        data = self.client_socket.receive_text()
        print("Данные полученные от сервера: ", data)

    def disconnect(self):
        # Close connection
        self.client_socket.close()
        print("Отключение от сервера.")


if __name__ == "__main__":
    host = input('Введите хост (по умолчанию - "localhost"): ') or 'localhost'
    port = input('Введите порт (по умолчанию - 12345): ')
    port = int(port) if port.isdigit() else 12345

    client = EchoClient(host, port)
    client.connect()

    while True:
        message = input("Введите сообщение или 'exit' для отключения): ")
        client.send_receive(message)
        if message == 'exit':
            break

    client.disconnect()
