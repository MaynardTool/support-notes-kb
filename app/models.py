# file: app/models.py
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_login_at = db.Column(db.DateTime, nullable=True)

    created_notes = db.relationship(
        "Note",
        foreign_keys="Note.created_by_id",
        back_populates="created_by",
        lazy="dynamic",
    )
    updated_notes = db.relationship(
        "Note",
        foreign_keys="Note.updated_by_id",
        back_populates="updated_by",
        lazy="dynamic",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


# Association table for notes and tags
note_tags = db.Table(
    "note_tags",
    db.Column(
        "note_id",
        db.String(36),
        db.ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)

    notes = db.relationship("Note", secondary=note_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"

    @staticmethod
    def get_or_create(name):
        name = name.strip().lower()
        if not name:
            return None
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        return tag


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(500), nullable=True, index=True)
    is_archived = db.Column(db.Boolean, default=False)
    note_metadata = db.Column(JSONB, default={})
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    search_vector = db.Column(TSVECTOR())

    created_by_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    updated_by_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    created_by = db.relationship(
        "User", foreign_keys=[created_by_id], back_populates="created_notes"
    )
    updated_by = db.relationship(
        "User", foreign_keys=[updated_by_id], back_populates="updated_notes"
    )
    tags = db.relationship("Tag", secondary=note_tags, back_populates="notes")

    __table_args__ = (
        db.Index("ix_notes_search_vector", "search_vector", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<Note {self.title}>"
