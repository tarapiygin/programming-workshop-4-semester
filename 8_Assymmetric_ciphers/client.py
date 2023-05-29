import socket
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from crypto_utils import (
    generate_key,
    load_keys,
    save_keys,
    decrypt,
    encrypt
)

PRIVATE_KEY_PATH = 'client_private_key.pem'
PUBLIC_KEY_PATH = 'client_public_key.pem'


def start_client(host='localhost', port=12345):
    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Загружаем ключи, если они были сохранены, иначе генерируем новые
    try:
        private_key, public_key = load_keys(private_path=PRIVATE_KEY_PATH,
                                            public_path=PUBLIC_KEY_PATH
                                            )
    except FileNotFoundError:
        private_key, public_key = generate_key()
        save_keys(private_key,
                  public_key,
                  private_path=PRIVATE_KEY_PATH,
                  public_path=PUBLIC_KEY_PATH
                  )

    # Подключаемся к серверу
    s.connect((host, port))
    print(f"Подключение к серверу на {host}:{port}")

    # Принимаем открытый ключ сервера
    server_public_key_pem = s.recv(1024)
    server_public_key = serialization.load_pem_public_key(
        server_public_key_pem,
        backend=default_backend())

    # Отправляем свой открытый ключ
    s.sendall(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))

    while True:
        # Вводим сообщение для отправки
        message = input("Enter a message to send: ").encode()

        # Шифруем сообщение
        encrypted_message = encrypt(server_public_key, message)

        # Отправляем зашифрованное сообщение
        s.sendall(encrypted_message)
        print("Encrypted message sent to server.")

        # Принимаем зашифрованное сообщение
        encrypted_message = s.recv(1024)
        print("Encrypted message received from server.")

        # Расшифровываем сообщение
        message = decrypt(private_key, encrypted_message)
        print(f"Decrypted message from server: {message.decode()}")

    s.close()
    print("Disconnected from server.")


if __name__ == "__main__":
    start_client()
