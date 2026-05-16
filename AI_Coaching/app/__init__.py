from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config
from app.extensions import db

csrf = CSRFProtect()


def create_app(config_class=Config):
    """Application factory used by Flask and tests."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)

    from app.auth.routes import auth_bp
    from app.candidate.routes import candidate_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app
