from functools import wraps

from flask import flash, redirect, session, url_for

from app.models import User


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = current_user()
            if not user or user.role not in roles:
                flash("You do not have permission to view that page.", "danger")
                return redirect(url_for("candidate.dashboard"))
            return view(*args, **kwargs)

        return wrapped_view

    return decorator
