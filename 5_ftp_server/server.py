import os
import socket
import threading
import file_manager
import datetime

# Настройка пути к рабочей директории на сервере
server_work_dir = os.path.abspath('./server_work_dir')

# Словарь для хранения пользователей и их файловых менеджеров
clients = {}
users = [('admin', '12345'), ('guest', 'guest')]

# Создаем словарь пользователей
user_fm = {}

# Создаем файловый менеджер для каждого пользователя
for user in users:
    username, password = user
    user_path = os.path.join(server_work_dir, username)
    os.makedirs(user_path, exist_ok=True)
    user_fm[user] = file_manager.FileManager(user_path, user_path)


def handle_client(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            current_user = user_fm[clients[client]]
            result = ''
            if msg == 'ls':
                result = '\n'.join(os.listdir(current_user.current_path))
            elif msg.startswith('cd '):
                folder_name = msg.split(' ')[1]
                current_user.change_directory(folder_name)
                result = f'Переход в папку {folder_name} выполнен.'
            elif msg == 'cd ..':
                current_user.move_up()
                result = 'Переход на уровень выше выполнен.'
            elif msg.startswith('mkdir '):
                folder_name = msg.split(' ')[1]
                current_user.create_folder(folder_name)
                result = f'Папка {folder_name} создана.'
            elif msg.startswith('rmdir '):
                folder_name = msg.split(' ')[1]
                current_user.delete_folder(folder_name)
                result = f'Папка {folder_name} удалена.'
            elif msg.startswith('rm '):
                file_name = msg.split(' ')[1]
                current_user.delete_file(file_name)
                result = f'Файл {file_name} удален.'
            elif msg.startswith('cp '):
                file_name, new_name = msg.split(' ')[1:]
                current_user.copy_file(file_name, new_name)
                result = f'Файл {file_name} скопирован в {new_name}.'
            elif msg.startswith('mv '):
                old_name, new_name = msg.split(' ')[1:]
                current_user.move_file(old_name, new_name)
                result = f'Файл {old_name} перемещен в {new_name}.'
            elif msg.startswith('rename '):
                old_name, new_name = msg.split(' ')[1:]
                current_user.rename_file(old_name, new_name)
                result = f'Файл {old_name} переименован в {new_name}.'
            elif msg.startswith('read '):
                file_name = msg.split(' ')[1]
                result = current_user.read_file(file_name)
            elif msg.startswith('sendfile '):
                file_name = msg.split(' ')[1]
                with open(file_name, 'wb') as f:
                    while True:
                        data = client.recv(1024)
                        if not data:
                            break
                        f.write(data)
                f.close()
                result = 'Файл успешно загружен на сервер'
            elif msg.startswith('getfile '):
                file_name = msg.split(' ')[1]
                f = open(file_name, 'rb')
                l = f.read(1024)
                while (l):
                    client.send(l)
                    l = f.read(1024)
                f.close()
            else:
                result = 'Непонятная команда.'

            # относительный путь от рабочей директории
            relative_path = os.path.relpath(current_user.current_path, current_user.working_directory)
            client.sendall((result + '\n' + 'Вы находитесь в: ' + relative_path).encode())

            # Логирование
            with open('server.log', 'a') as f:
                f.write(f'{datetime.datetime.now()} - User: {clients[client]} - Command: {msg}\n')
        except:
            del clients[client]
            client.close()
            break


def start_server(host='localhost', port=12345):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("FTP сервер запущен.")
    s.bind((host, port))
    print(f"Слушаем на {host}:{port}")
    s.listen(10)
    print("Ожидаем подключения...")

    while True:
        conn, addr = s.accept()
        conn.sendall('Введите имя: '.encode())
        username = conn.recv(1024).decode()
        conn.sendall('Введите пароль: '.encode())
        password = conn.recv(1024).decode()
        if (username, password) in user_fm:
            conn.sendall('Вы успешно подключились к FTP серверу!\n'.encode())
            clients[conn] = (username, password)
            client_thread = threading.Thread(target=handle_client, args=(conn,))
            client_thread.start()
        else:
            conn.sendall('Неправильное имя или пароль. Соединение закрывается.\n'.encode())
            conn.close()

    s.close()
    print("FTP сервер остановлен.")


if __name__ == "__main__":
    start_server()
