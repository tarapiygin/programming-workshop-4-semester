import logging
import socket
import sqlite3
import bcrypt
from socket_extension import ExtendedSocket

BASE_COMMANDS = 'Отправьте:\n' \
                '1 - для входа\n' \
                '2 - для регистрации\n'

WELCOME_MESSAGE = 'Привет! Я сервер эхо с аутентификацией!.\n'


class Server:

    def __init__(self, host='localhost', port=12345, db_path='users.db'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.server_socket = None

        # Создаем журнал
        logging.basicConfig(filename='server.log', level=logging.INFO)
        self.logger = logging.getLogger()

        # Создаем или подключаемся к базе данных
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT)''')

    def registry(self, client_conn):
        client_conn.send_text(
            'Привет! Пожалуйста, зарегистрируйтесь с вашим именем пользователя и паролем.\nВведите имя пользователя:')
        username = client_conn.receive_text()
        self.cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        user = self.cursor.fetchone()
        if user:
            client_conn.send_text('Это имя пользователя уже занято!')
            return False
        client_conn.send_text('Замечательно! Введите пароль:')
        password = client_conn.receive_text().encode()
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        self.cursor.execute('INSERT INTO users VALUES (?, ?)', (username, hashed.decode()))
        self.conn.commit()
        client_conn.send_text('Регистрация прошла успешно! Добро пожаловать!')
        return True

    def auth(self, client_conn):
        # Получаем пользователя из базы данных
        client_conn.send_text('Пожалуйста, введите ваше имя пользователя:')
        username = client_conn.receive_text()
        self.cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        user = self.cursor.fetchone()
        if not user:
            client_conn.send_text('Это имя пользователя не зарегистрировано.\n' + BASE_COMMANDS)
            return False

        if user:
            client_conn.send_text(f'Привет, {user[0]}! Пожалуйста, введите ваш пароль:')
            password = client_conn.receive_text().encode()
            if bcrypt.checkpw(password, user[1].encode()):
                client_conn.send_text('Добро пожаловать обратно!')
                return True
            else:
                client_conn.send_text('Неправильный пароль!\n' + BASE_COMMANDS)
                # client_conn.close()

        return False

    def start(self):
        # Создаем сокет
        self.server_socket = ExtendedSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.info('Сервер запущен.')
        # Привязываем сокет к хосту и порту
        try:
            self.server_socket.bind((self.host, self.port))
        except OSError as e:
            self.logger.error(f'Порт {self.port} уже используется. Ошибка: {str(e)}')
            self.port += 1
            self.start()
            return

        self.logger.info(f'Прослушивание на {self.host}:{self.port}')

        # Прослушивание
        self.server_socket.listen(1)
        self.logger.info('Ожидание подключений...')

        while True:
            # Принимаем подключение
            client_sock, addr = self.server_socket.accept()
            # Обертываем возвращенный сокет в наш расширенный класс сокета
            client_conn = ExtendedSocket(fileno=client_sock.fileno())
            self.logger.info(f'Клиент подключен: {addr}')

            client_messages = 0
            user_auth = False
            while True:
                # Получаем данные от клиента
                data = client_conn.receive_text()
                self.logger.info('Получены данные от клиента.')
                if not data or data == 'exit':
                    # Если нет данных или клиент хочет выйти
                    self.logger.info(f'Клиент отключился: {addr}')
                    break
                if data == '1':
                    # Просим логин и пароль
                    user_auth = self.auth(client_conn)
                    continue
                if data == '2':
                    # Отправляем на регистрацию
                    user_auth = self.registry(client_conn)
                    continue
                # Отправляем данные обратно клиенту в зависимости от его авторизации
                if user_auth:
                    client_conn.send_text(f'Ваше сообщение: {data}\n')
                elif client_messages != 0:
                    client_conn.send_text(f'Ваше сообщение: {data}\n {BASE_COMMANDS}')
                elif client_messages == 0:
                    client_conn.send_text(f'{WELCOME_MESSAGE}{BASE_COMMANDS}Ваше сообщение: {data}\n')
                self.logger.info('Данные отправлены обратно клиенту.')

            client_conn.close()

    def stop(self):
        self.server_socket.close()
        self.logger.info('Сервер остановлен.')
        self.conn.close()


if __name__ == '__main__':
    host = input('Введите хост (по умолчанию - "localhost"): ') or 'localhost'
    port = input('Введите порт (по умолчанию - 12345): ')
    port = int(port) if port.isdigit() else 12345

    server = Server(host, port)
    server.start()
