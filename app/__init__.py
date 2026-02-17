# file: app/__init__.py
from flask import Flask
from app.config import config
from app.extensions import db, login_manager, migrate, csrf
from app.models import User


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    from app.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from app.notes import notes as notes_blueprint

    app.register_blueprint(notes_blueprint)

    from app.tags import tags as tags_blueprint

    app.register_blueprint(tags_blueprint, url_prefix="/tags")

    from app.admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from app.cli import create_admin, import_files, import_onenote

    app.cli.add_command(create_admin)
    app.cli.add_command(import_files)
    app.cli.add_command(import_onenote)

    return app
