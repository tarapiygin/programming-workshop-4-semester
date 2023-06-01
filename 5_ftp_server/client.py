import socket


def start_client(host='localhost', port=12345):
    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Устанавливаем соединение с сервером
    s.connect((host, port))
    print(f"Соединение с сервером {host}:{port}")
    data = s.recv(1024)
    print("Данные полученные от сервера: ", data.decode())

    while True:
        # Получаем данные от пользователя
        message = input("Введите сообщение: ")
        # Отправляем данные серверу
        s.sendall(message.encode())
        print("Данные отправлены серверу.")

        # Check if client wants to send or receive a file
        if message.startswith('sendfile '):
            file_name = message.split(' ')[1]
            f = open(file_name, 'rb')
            l = f.read(1024)
            while (l):
                s.send(l)
                l = f.read(1024)
            f.close()
            print('Отправка файла завершена')
        elif message.startswith('getfile '):
            file_name = message.split(' ')[1]
            with open(file_name, 'wb') as f:
                print('файл создан')
                m = 'получение данных.'
                while True:
                    if m[-3] == '.':
                        m = 'получение данных.'
                    m += '.'
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
                    print(m)
            f.close()
            print('Получение файла завершено')
        elif message == 'exit':
            s.close()
            break

        # Получаем ответ от сервера
        data = s.recv(1024)
        print("Данные полученные от сервера: ", data.decode())

    # Закрываем соединение
    s.close()
    print("Отлючение от сервера.")


if __name__ == "__main__":
    start_client()
