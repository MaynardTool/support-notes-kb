# file: app/tags/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.tags import tags
from app.extensions import db
from app.models import Tag


@tags.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    if search:
        tag_query = Tag.query.filter(Tag.name.ilike(f"%{search}%"))
    else:
        tag_query = Tag.query

    all_tags = tag_query.order_by(Tag.name).all()

    tags_with_counts = []
    for tag in all_tags:
        tags_with_counts.append({"tag": tag, "note_count": len(tag.notes)})

    return render_template(
        "tags/index.html", tags_with_counts=tags_with_counts, search=search
    )


@tags.route("/<int:tag_id>/edit", methods=["GET", "POST"])
@login_required
def edit(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    if request.method == "POST":
        new_name = request.form.get("name", "").strip().lower()
        if not new_name:
            flash("Tag name cannot be empty.", "danger")
            return redirect(url_for("tags.edit", tag_id=tag_id))

        existing = Tag.query.filter_by(name=new_name).first()
        if existing and existing.id != tag.id:
            flash("A tag with this name already exists.", "danger")
            return redirect(url_for("tags.edit", tag_id=tag_id))

        tag.name = new_name
        db.session.commit()
        flash("Tag updated successfully!", "success")
        return redirect(url_for("tags.index"))

    return render_template("tags/edit.html", tag=tag)


@tags.route("/<int:tag_id>/delete", methods=["POST"])
@login_required
def delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    note_count = len(tag.notes)

    if note_count > 0:
        flash(
            f'Cannot delete tag "{tag.name}" because it is used by {note_count} note(s). Remove the tag from those notes first.',
            "warning",
        )
        return redirect(url_for("tags.index"))

    db.session.delete(tag)
    db.session.commit()
    flash("Tag deleted successfully!", "success")
    return redirect(url_for("tags.index"))
