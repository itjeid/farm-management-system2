from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access the system.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access the system.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("Administrator access is required.", "danger")
            return redirect(url_for("dashboard.dashboard"))
        return view(*args, **kwargs)
    return wrapped_view


def _user_can_login(user):
    return user and user.role in {"admin", "user"}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not _user_can_login(user):
                status = "waiting for administrator approval" if user.role == "pending" else "revoked"
                flash(f"This account is {status}. Please contact the administrator.", "warning")
                return render_template("login.html")
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(username) < 3 or len(password) < 6:
            flash("Username must have at least 3 characters and password at least 6 characters.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(username=username).first():
            flash("That username already exists.", "danger")
        else:
            user = User(username=username, role="pending")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. An administrator must grant access before you can sign in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


def create_admin():
    existing_admin = User.query.filter_by(username="admin").first()
    if existing_admin:
        return
    admin = User(username="admin", role="admin")
    admin.set_password("Admin@123")
    db.session.add(admin)
    db.session.commit()
