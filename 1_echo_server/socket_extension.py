import socket


class ExtendedSocket(socket.socket):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_text(self, message):
        # Преобразуем сообщение в байты и добавляем впереди его длину
        message = bytes(f"{len(message):<{10}}", 'utf-8') + bytes(message, 'utf-8')
        self.sendall(message)

    def receive_text(self):
        # Получаем длину сообщения
        message_length = int(self.recv(10).strip())
        # Получаем сообщение
        message = self.recv(message_length).decode()
        return message
