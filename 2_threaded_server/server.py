import socket
import threading

# Dict для хранения авторизованных пользователей
clients = {}
# Кортеж пароль и логин для демонстрации
users = [('admin', '12345'), ('guest', 'guest')]


def broadcast(msg, _from):
    # Рассылка сообщения всем клиентам
    for client in clients:
        if client != _from:
            try:
                client.sendall(msg.encode())
            except:
                client.close()
                del clients[client]


def handle_client(client):
    while True:
        try:
            # Попытка получения сообщения
            msg = client.recv(1024).decode()
            broadcast(f'{clients[client]}: {msg}', client)
        except:
            # Если что-то пойдет не так, клиент будет удален
            del clients[client]
            broadcast(f'{clients[client]} left the chat!', client)
            client.close()
            break


def start_server(host='localhost', port=12345):
    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Сервер запущен.")

    # Привязываем сокет к хосту и порту
    s.bind((host, port))
    print(f"Слушаем на {host}:{port}")

    # Переводим сокет в режим прослушивания
    s.listen(10)
    print("Ожидаем подключения...")

    while True:
        # Принимаем соединение
        conn, addr = s.accept()
        # Запрашиваем имя пользователя и пароль
        conn.sendall('Введите имя: '.encode())
        username = conn.recv(1024).decode()
        conn.sendall('Введите пароль: '.encode())
        password = conn.recv(1024).decode()

        if (username, password) in users:
            conn.sendall('Добро пожаловать в чат!\n'.encode())
            clients[conn] = username
            broadcast(f'{username} присоеденился к чату!', conn)

            # Создаем и запускаем новый поток, который будет обрабатывать подключение
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.start()
        else:
            conn.sendall('Неправильное имя или пароль. Соединения закрывается.\n'.encode())
            conn.close()

    s.close()
    print("Сервер остановлен.")


if __name__ == "__main__":
    start_server()
