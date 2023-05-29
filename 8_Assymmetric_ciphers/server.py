import socket
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from crypto_utils import (
    generate_key,
    save_keys,
    load_keys,
    decrypt,
    encrypt
)

PRIVATE_KEY_PATH = 'server_private_key.pem'
PUBLIC_KEY_PATH = 'server_public_key.pem'


def start_server(host='localhost', port=12345):
    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Сервер запущен.")

    # Привязываем сокет к хосту и порту
    s.bind((host, port))
    print(f"Слушаем на {host}:{port}")

    # Переводим сокет в режим прослушивания
    s.listen(1)
    print("Ожидаем подключения...")

    # Загружаем ключи, если они были сохранены, иначе генерируем новые
    try:
        private_key, public_key = load_keys(
            private_path=PRIVATE_KEY_PATH,
            public_path=PUBLIC_KEY_PATH
        )
    except FileNotFoundError:
        private_key, public_key = generate_key()
        save_keys(private_key,
                  public_key,
                  private_path=PRIVATE_KEY_PATH,
                  public_path=PUBLIC_KEY_PATH
                  )

    while True:
        # Принимаем соединение
        conn, addr = s.accept()
        print(f"Подключен клиент: {addr}")

        # Отправляем открытый ключ
        conn.sendall(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo))

        # Принимаем открытый ключ клиента
        client_public_key_pem = conn.recv(1024)
        client_public_key = serialization.load_pem_public_key(
            client_public_key_pem,
            backend=default_backend())

        while True:
            # Принимаем зашифрованные данные от клиента
            encrypted_data = conn.recv(1024)
            print("Получены зашифрованные данные от клиента.")

            if not encrypted_data:
                # Если данных нет, клиент отключился
                print(f"Клиент отключен: {addr}")
                break

            # Расшифровываем данные
            data = decrypt(private_key, encrypted_data)

            # Шифруем данные обратно клиенту
            encrypted_data = encrypt(client_public_key, data)
            conn.sendall(encrypted_data)
            print("Зашифрованные данные отправлены обратно клиенту.")

        conn.close()
    s.close()
    print("Сервер остановлен.")


if __name__ == "__main__":
    start_server()
