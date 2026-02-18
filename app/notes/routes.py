# file: app/notes/routes.py
import logging
from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from app.notes import notes
from app.notes.forms import NoteForm, DeleteNoteForm, ArchiveNoteForm
from app.extensions import db
from app.models import Note, Tag
from app.utils.markdown import render_markdown

logger = logging.getLogger(__name__)


@notes.route("/")
@login_required
def index():
    query = request.args.get("q", "").strip()
    tag_names = request.args.getlist("tag")
    include_archived = request.args.get("archived", "0") == "1"
    sort = request.args.get("sort", "updated_desc")

    note_query = Note.query

    if not include_archived:
        note_query = note_query.filter_by(is_archived=False)

    if query:
        search_query = func.plainto_tsquery("english", query)
        note_query = note_query.filter(Note.search_vector.op("@@")(search_query))
        note_query = note_query.order_by(
            func.ts_rank(Note.search_vector, search_query).desc()
        )
    else:
        if sort == "updated_desc":
            note_query = note_query.order_by(Note.updated_at.desc())
        elif sort == "updated_asc":
            note_query = note_query.order_by(Note.updated_at.asc())
        elif sort == "title_asc":
            note_query = note_query.order_by(Note.title.asc())
        elif sort == "title_desc":
            note_query = note_query.order_by(Note.title.desc())
        elif sort == "created_desc":
            note_query = note_query.order_by(Note.created_at.desc())

    if tag_names:
        for tag_name in tag_names:
            note_query = note_query.filter(Note.tags.any(Tag.name == tag_name.lower()))

    notes_list = note_query.all()
    all_tags = Tag.query.order_by(Tag.name).all()

    return render_template(
        "notes/index.html",
        notes=notes_list,
        all_tags=all_tags,
        query=query,
        selected_tags=tag_names,
        include_archived=include_archived,
        sort=sort,
    )


@notes.route("/notes/new", methods=["GET", "POST"])
@login_required
def new():
    logger.info(f"User {current_user.email} accessing new note form")
    form = NoteForm()

    if form.validate_on_submit():
        logger.info(f"Creating new note: {form.title.data} by {current_user.email}")
        note = Note(
            title=form.title.data,
            body=form.body.data,
            summary=form.summary.data,
            source=form.source.data,
            created_by_id=current_user.id,
            updated_by_id=current_user.id,
        )

        tags_input = form.tags.data or ""
        tag_names = [t.strip().lower() for t in tags_input.split(",") if t.strip()]
        for tag_name in set(tag_names):
            tag = Tag.get_or_create(tag_name)
            if tag:
                note.tags.append(tag)

        db.session.add(note)
        db.session.commit()

        logger.info(f"Note created successfully: {note.id}")

        flash("Note created successfully!", "success")
        return redirect(url_for("notes.view", note_id=note.id))

    logger.debug(f"Form validation failed: {form.errors}")
    return render_template("notes/edit.html", form=form, action="Create")


@notes.route("/notes/<note_id>", methods=["GET"])
@login_required
def view(note_id):
    note = Note.query.get_or_404(note_id)
    rendered_body = render_markdown(note.body)

    return render_template("notes/view.html", note=note, rendered_body=rendered_body)


@notes.route("/notes/<note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    note = Note.query.get_or_404(note_id)
    logger.info(f"User {current_user.email} editing note: {note.id}")
    form = NoteForm(obj=note)

    if form.validate_on_submit():
        logger.info(f"Updating note: {note.id} by {current_user.email}")
        note.title = form.title.data
        note.body = form.body.data
        note.summary = form.summary.data
        note.source = form.source.data
        note.updated_by_id = current_user.id
        note.updated_at = datetime.now(timezone.utc)

        note.tags.clear()
        tags_input = form.tags.data or ""
        tag_names = [t.strip().lower() for t in tags_input.split(",") if t.strip()]
        for tag_name in set(tag_names):
            tag = Tag.get_or_create(tag_name)
            if tag:
                note.tags.append(tag)

        db.session.commit()

        logger.info(f"Note updated successfully: {note.id}")

        flash("Note updated successfully!", "success")
        return redirect(url_for("notes.view", note_id=note.id))

    if not form.tags.data:
        form.tags.data = ", ".join([t.name for t in note.tags])

    return render_template("notes/edit.html", form=form, action="Edit", note=note)


@notes.route("/notes/<note_id>/delete", methods=["GET", "POST"])
@login_required
def delete(note_id):
    note = Note.query.get_or_404(note_id)
    form = DeleteNoteForm()

    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()
        flash("Note deleted successfully!", "success")
        return redirect(url_for("notes.index"))

    return render_template("notes/confirm_delete.html", form=form, note=note)


@notes.route("/notes/<note_id>/archive", methods=["POST"])
@login_required
def toggle_archive(note_id):
    note = Note.query.get_or_404(note_id)
    note.is_archived = not note.is_archived
    note.updated_at = datetime.now(timezone.utc)
    note.updated_by_id = current_user.id
    db.session.commit()

    status = "archived" if note.is_archived else "unarchived"
    flash(f"Note {status} successfully!", "success")

    return redirect(url_for("notes.view", note_id=note.id))
