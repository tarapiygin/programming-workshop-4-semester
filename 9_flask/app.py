from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_sslify import SSLify
import os
from datetime import datetime

# инициализируем приложение Flask
app = Flask(__name__)

# устанавливаем путь к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# инициализируем объект SQLAlchemy для работы с базой данных
db = SQLAlchemy(app)

# включаем SSL только на продакшене
if 'GAE_INSTANCE' in os.environ:
    sslify = SSLify(app)


# определяем модель пользователя в базе данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.username


# определяем endpoint для создания нового пользователя
@app.route('/user/', methods=['POST'])
def create_user():
    # получаем данные из POST-запроса
    data = request.get_json()

    # извлекаем из данных логин и пароль
    username = data.get('username')
    password = data.get('password')

    # проверяем наличие логина и пароля
    if username and password:
        # хешируем пароль
        hashed_password = generate_password_hash(password)

        # создаем нового пользователя
        new_user = User(username=username, password=hashed_password)

        # добавляем пользователя в базу данных
        db.session.add(new_user)
        db.session.commit()

        # отправляем ответ, что пользователь успешно создан
        return jsonify({"message": "user created"}), 201
    else:
        # если логин и/или пароль отсутствуют, отправляем соответствующее сообщение
        return jsonify({"message": "username and password required"}), 400


# определяем endpoint для получения информации о пользователе
@app.route('/user/<username>/', methods=['GET'])
def get_user(username):
    # ищем пользователя в базе данных
    user = User.query.filter_by(username=username).first()

    # если пользователь найден, отправляем информацию о нем
    if user:
        return jsonify({"username": user.username, "registration_date": user.registration_date}), 200
    else:
        # если пользователь не найден, отправляем соответствующее сообщение
        return jsonify({"message": "user not found"}), 404


with app.app_context():
    # создаем все необходимые таблицы в базе данных
    db.create_all()

# запускаем приложение
if __name__ == '__main__':
    # запускаем приложение
    app.run(debug=True)
