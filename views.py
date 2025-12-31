from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import StudySession, Task

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return redirect(url_for("main.dashboard"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    sessions = (StudySession.query
                .filter_by(user_id=current_user.id)
                .order_by(StudySession.started_at.desc())
                .limit(10)
                .all())

    tasks = (Task.query
             .filter_by(user_id=current_user.id)
             .order_by(Task.created_at.desc())
             .limit(10)
             .all())

    sessions_count = StudySession.query.filter_by(user_id=current_user.id).count()
    tasks_count = Task.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "dashboard.html",
        sessions_count=sessions_count,
        tasks_count=tasks_count,
        sessions=sessions,
        tasks=tasks
    )

@main_bp.route("/sessions/new", methods=["POST"])
@login_required
def create_session():
    subject = request.form.get("subject", "").strip()
    duration = request.form.get("duration_minutes", "").strip()
    focus = request.form.get("focus_rating", "").strip()

    if not subject:
        flash("Subject is required.")
        return redirect(url_for("main.dashboard"))

    try:
        duration_int = int(duration)
        focus_int = int(focus)
    except ValueError:
        flash("Duration and focus must be numbers.")
        return redirect(url_for("main.dashboard"))

    if duration_int <= 0:
        flash("Duration must be greater than 0.")
        return redirect(url_for("main.dashboard"))

    if focus_int < 1 or focus_int > 5:
        flash("Focus rating must be between 1 and 5.")
        return redirect(url_for("main.dashboard"))

    session = StudySession(
        user_id=current_user.id,
        subject=subject,
        duration_minutes=duration_int,
        focus_rating=focus_int
    )
    db.session.add(session)
    db.session.commit()

    flash("Study session added.")
    return redirect(url_for("main.dashboard"))

@main_bp.route("/tasks/new", methods=["POST"])
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Task title is required.")
        return redirect(url_for("main.dashboard"))

    task = Task(user_id=current_user.id, title=title)
    db.session.add(task)
    db.session.commit()

    flash("Task added.")
    return redirect(url_for("main.dashboard"))

@main_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Task not found.")
        return redirect(url_for("main.dashboard"))

    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id: int):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Task not found.")
        return redirect(url_for("main.dashboard"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.")
    return redirect(url_for("main.dashboard"))

