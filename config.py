# config.py


class Config:
    # Secret key for securely signing the session cookie and other security-related purposes
    SECRET_KEY = "42e76d8053493a28cc90a625d2315d2666da0c445351d01c5ddb8ba8aaa71f55"

    # URI for the SQLite database used in the application
    SQLALCHEMY_DATABASE_URI = "sqlite:///todo.db"

    # Disable modification tracking to save resources; useful in larger applications
    SQLALCHEMY_TRACK_MODIFICATIONS = False
