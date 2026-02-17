# file: app/notes/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=255)])
    body = TextAreaField("Body", validators=[DataRequired()])
    summary = StringField("Summary")
    source = StringField("Source")
    tags = StringField("Tags (comma-separated)")
    submit = SubmitField("Save Note")


class DeleteNoteForm(FlaskForm):
    submit = SubmitField("Delete Note")


class ArchiveNoteForm(FlaskForm):
    submit = SubmitField("Toggle Archive")
