import os
import socket
import threading
import mimetypes
import datetime
from urllib.parse import unquote
from settings import PORT, MAX_REQUEST_SIZE, ALLOWED_FILE_TYPES, WORK_DIR

# Разделитель строк в HTTP
CRLF = "\r\n"


class ClientThread(threading.Thread):
    # Инициализация потока для обслуживания клиента
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        # Чтение данных от клиента
        request = self.conn.recv(MAX_REQUEST_SIZE).decode()

        # Извлечение информации о запрашиваемом файле
        path = unquote(request.split(" ")[1])

        # Убедимся, что путь начинается со слеша
        if not path.startswith("/"):
            path = "/" + path

        # Обработка запроса
        self.handle_request(path)

    def handle_request(self, path):
        # Полный путь к запрашиваемому файлу
        full_path = os.path.join(WORK_DIR, path[1:])

        if not os.path.exists(full_path):
            # Если файл не найден, отправляем ошибку 404
            self.send_error(404, "File not found")
        elif not os.path.isfile(full_path):
            # Если это не файл, отправляем ошибку 403
            self.send_error(403, "Forbidden")
        else:
            # Проверяем тип файла
            file_type = full_path.split(".")[-1]
            if file_type not in ALLOWED_FILE_TYPES:
                # Если тип файла не разрешен, отправляем ошибку 403
                self.send_error(403, "Forbidden")
            else:
                # Если все в порядке, отправляем файл
                self.send_file(full_path)

    def send_file(self, path):
        # Отправка файла клиенту
        with open(path, "rb") as fp:
            content = fp.read()
        content_length = len(content)
        content_type, _ = mimetypes.guess_type(path)
        date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        response_line = "HTTP/1.1 200 OK"
        headers = [
            f"Date: {date}",
            f"Server: SimplePythonServer",
            f"Content-Length: {content_length}",
            f"Content-Type: {content_type}",
            f"Connection: close",
        ]
        response_headers = CRLF.join([response_line, *headers, "", ""])
        self.conn.sendall(response_headers.encode())
        self.conn.sendall(content)

    def send_error(self, status_code, message):
        # Отправка сообщения об ошибке
        response_line = f"HTTP/1.1 {status_code} {message}"
        headers = [
            f"Date: {datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}",
            f"Server: SimplePythonServer",
            f"Content-Type: text/html",
            f"Connection: close",
        ]
        response_body = f"<h1>{status_code} {message}</h1>"
        headers.append(f"Content-Length: {len(response_body)}")
        response_headers = CRLF.join([response_line, *headers, "", ""])
        self.conn.sendall(response_headers.encode())
        self.conn.sendall(response_body.encode())


def start_server():
    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Сервер запущен.")

    # Привязываем сокет к порту
    s.bind(("", PORT))
    print(f"Слушаем порт {PORT}")

    # Переводим сокет в режим прослушивания
    s.listen()
    print("Ожидаем подключений...")

    while True:
        # Принимаем подключение
        conn, addr = s.accept()
        print(f"Клиент подключился: {addr}")

        # Создаем и запускаем поток для обслуживания клиента
        ClientThread(conn, addr).start()


if __name__ == "__main__":
    start_server()
