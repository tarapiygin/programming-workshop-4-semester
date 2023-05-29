import socket


def start_client(host='localhost', port=12345):
    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Устанавливаем соединение с сервером
    s.connect((host, port))
    print(f"Соединение с сервером {host}:{port}")

    while True:
        # Получаем данные от пользователя
        message = input("Введите сообщение: ")
        # Отправляем данные серверу
        s.sendall(message.encode())
        print("Данные отправлены серверу.")

        # Получаем ответ от сервера
        data = s.recv(1024)
        print("Данные полученные от сервера: ", data.decode())

    # Закрываем соединение
    s.close()
    print("Отлючение от сервера.")


if __name__ == "__main__":
    start_client()