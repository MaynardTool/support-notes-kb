# file: tests/test_search.py
from app.extensions import db
from app.models import Note, User, Tag


def test_search_notes(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        note1 = Note(
            title="PostgreSQL Setup",
            body="How to install and configure PostgreSQL database",
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        note2 = Note(
            title="Redis Cache",
            body="Using Redis for caching in Python applications",
            created_by_id=user.id,
            updated_by_id=user.id,
        )

        db.session.add(note1)
        db.session.add(note2)
        db.session.commit()

        response = logged_in_client.get("/?q=PostgreSQL")
        assert response.status_code == 200
        assert b"PostgreSQL Setup" in response.data


def test_search_no_results(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        note = Note(
            title="Some Note",
            body="Some content",
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        db.session.add(note)
        db.session.commit()

        response = logged_in_client.get("/?q=nonexistent")
        assert response.status_code == 200
        assert b"No notes found" in response.data


def test_filter_by_tag(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        tag = Tag(name="database")
        db.session.add(tag)

        note1 = Note(
            title="DB Note 1",
            body="Content 1",
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        note1.tags.append(tag)

        note2 = Note(
            title="Other Note",
            body="Content 2",
            created_by_id=user.id,
            updated_by_id=user.id,
        )

        db.session.add(note1)
        db.session.add(note2)
        db.session.commit()

        response = logged_in_client.get("/?tag=database")
        assert response.status_code == 200
        assert b"DB Note 1" in response.data


def test_include_archived(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        archived_note = Note(
            title="Archived Note",
            body="This is archived",
            is_archived=True,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        db.session.add(archived_note)
        db.session.commit()

        response = logged_in_client.get("/")
        assert response.status_code == 200
        assert b"Archived Note" not in response.data

        response = logged_in_client.get("/?archived=1")
        assert response.status_code == 200
        assert b"Archived Note" in response.data
