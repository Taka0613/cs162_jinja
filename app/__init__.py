from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .utils import generate_csrf_token  # Import the CSRF generator function

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .auth import auth as auth_blueprint
    from .routes import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    # Add CSRF token generator to the Jinja environment
    app.jinja_env.globals["csrf_token"] = generate_csrf_token

    with app.app_context():
        db.create_all()

    return app
