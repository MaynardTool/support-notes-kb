# file: app/auth/routes.py
from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("notes.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash(
                    "Your account has been deactivated. Please contact an administrator.",
                    "danger",
                )
                return render_template("auth/login.html", form=form)

            login_user(user)
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()

            next_page = request.args.get("next")
            flash(f"Welcome back, {user.display_name}!", "success")
            return redirect(next_page or url_for("notes.index"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if not current_app.config.get("ALLOW_SELF_REGISTER", False):
        flash("Self-registration is not enabled.", "warning")
        return redirect(url_for("auth.login"))

    if current_user.is_authenticated:
        return redirect(url_for("notes.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return render_template("auth/register.html", form=form)

        user = User(
            email=form.email.data,
            display_name=form.display_name.data,
            is_admin=False,
            is_active=True,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)
