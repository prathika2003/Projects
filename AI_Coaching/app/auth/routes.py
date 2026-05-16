from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("candidate.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "candidate")

        if role not in {"candidate", "admin"}:
            role = "candidate"

        if not name or len(password) < 8:
            flash("Name is required and password must be at least 8 characters.", "danger")
            return render_template("auth/register.html")

        try:
            email = validate_email(email).normalized
        except EmailNotValidError:
            flash("Please enter a valid email address.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("An account already exists for that email.", "danger")
            return render_template("auth/register.html")

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        session.clear()
        session["user_id"] = user.id
        session["user_role"] = user.role
        flash("Welcome back.", "success")
        return redirect(url_for("candidate.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
