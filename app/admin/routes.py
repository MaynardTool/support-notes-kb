# file: app/admin/routes.py
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.admin import admin
from app.admin.forms import UserForm, ResetPasswordForm
from app.extensions import db
from app.models import User


def admin_required():
    if not current_user.is_admin:
        abort(403)


@admin.route("/users")
@login_required
def users():
    admin_required()

    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin.route("/users/new", methods=["GET", "POST"])
@login_required
def new_user():
    admin_required()

    form = UserForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("A user with this email already exists.", "danger")
            return redirect(url_for("admin.new_user"))

        user = User(
            email=form.email.data,
            display_name=form.display_name.data,
            is_admin=form.is_admin.data,
            is_active=form.is_active.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(f'User "{user.display_name}" created successfully!', "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_new.html", form=form)


@admin.route("/users/<user_id>/deactivate", methods=["POST"])
@login_required
def deactivate_user(user_id):
    admin_required()

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("admin.users"))

    user.is_active = False
    db.session.commit()
    flash(f'User "{user.display_name}" has been deactivated.', "success")
    return redirect(url_for("admin.users"))


@admin.route("/users/<user_id>/activate", methods=["POST"])
@login_required
def activate_user(user_id):
    admin_required()

    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash(f'User "{user.display_name}" has been activated.', "success")
    return redirect(url_for("admin.users"))


@admin.route("/users/<user_id>/reset-password", methods=["GET", "POST"])
@login_required
def reset_password(user_id):
    admin_required()

    user = User.query.get_or_404(user_id)
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(f'Password for "{user.display_name}" has been reset.', "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_edit.html", form=form, user=user)
