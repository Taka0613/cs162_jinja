# config.py
class Config:
    SECRET_KEY = "42e76d8053493a28cc90a625d2315d2666da0c445351d01c5ddb8ba8aaa71f55"
    SQLALCHEMY_DATABASE_URI = "sqlite:///todo.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
