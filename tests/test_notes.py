# file: tests/test_notes.py
from app.extensions import db
from app.models import Note, User


def test_create_note(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        response = logged_in_client.post(
            "/notes/new",
            data={
                "title": "Test Note",
                "body": "# Test Content\n\nThis is a test.",
                "summary": "A test summary",
                "tags": "test, sample",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Test Note" in response.data

        note = Note.query.filter_by(title="Test Note").first()
        assert note is not None
        assert note.body == "# Test Content\n\nThis is a test."
        assert len(note.tags) == 2


def test_view_note(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        note = Note(
            title="View Test",
            body="Test body",
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        db.session.add(note)
        db.session.commit()

        response = logged_in_client.get(f"/notes/{note.id}")
        assert response.status_code == 200
        assert b"View Test" in response.data


def test_edit_note(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        note = Note(
            title="Original Title",
            body="Original body",
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        db.session.add(note)
        db.session.commit()
        note_id = note.id

        response = logged_in_client.post(
            f"/notes/{note_id}/edit",
            data={"title": "Updated Title", "body": "Updated body", "tags": ""},
            follow_redirects=True,
        )

        assert response.status_code == 200

        updated_note = Note.query.get(note_id)
        assert updated_note.title == "Updated Title"


def test_delete_note(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        note = Note(
            title="To Delete",
            body="Will be deleted",
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        db.session.add(note)
        db.session.commit()
        note_id = note.id

        response = logged_in_client.post(
            f"/notes/{note_id}/delete",
            data={"submit": "Delete Note"},
            follow_redirects=True,
        )

        assert response.status_code == 200

        deleted_note = Note.query.get(note_id)
        assert deleted_note is None


def test_archive_note(logged_in_client, app):
    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()

        note = Note(
            title="Archive Test",
            body="Test body",
            is_archived=False,
            created_by_id=user.id,
            updated_by_id=user.id,
        )
        db.session.add(note)
        db.session.commit()
        note_id = note.id

        response = logged_in_client.post(
            f"/notes/{note_id}/archive", follow_redirects=True
        )

        assert response.status_code == 200

        updated_note = Note.query.get(note_id)
        assert updated_note.is_archived == True
