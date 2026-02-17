# file: tests/conftest.py
import pytest
import os
from app import create_app
from app.extensions import db
from app.models import User, Note, Tag


@pytest.fixture
def app():
    os.environ.setdefault(
        "DATABASE_URL", "postgresql://notesuser:notespass@localhost:5432/notesdb_test"
    )

    app = create_app("development")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        admin = User(
            email="admin@test.com",
            display_name="Admin User",
            is_admin=True,
            is_active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)

        user = User(
            email="user@test.com",
            display_name="Test User",
            is_admin=False,
            is_active=True,
        )
        user.set_password("user123")
        db.session.add(user)

        db.session.commit()

        yield app

        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(app, client):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

    with client.session_transaction() as sess:
        sess["_user_id"] = user.id

    return client


@pytest.fixture
def admin_client(app, client):
    with app.app_context():
        user = User.query.filter_by(email="admin@test.com").first()

    with client.session_transaction() as sess:
        sess["_user_id"] = user.id

    return client
