from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import StudySession, Task

# Blueprint MUST be defined before routes
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return redirect(url_for("main.dashboard"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # recent items
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

    # -------- weekly stats --------
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)

    week_sessions = (StudySession.query
                     .filter(
                         StudySession.user_id == current_user.id,
                         StudySession.started_at >= week_start
                     )
                     .all())

    minutes_this_week = sum(s.duration_minutes for s in week_sessions)
    days_studied = len({s.started_at.date() for s in week_sessions})

    avg_focus = None
    if week_sessions:
        avg_focus = round(
            sum(s.focus_rating for s in week_sessions) / len(week_sessions),
            2
        )

    # minutes by subject
    subject_minutes = {}
    for s in week_sessions:
        subject_minutes[s.subject] = subject_minutes.get(s.subject, 0) + s.duration_minutes

    subject_minutes_sorted = sorted(
        subject_minutes.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # best subject by focus
    best_subject = None
    if week_sessions:
        focus_sum = {}
        focus_count = {}
        for s in week_sessions:
            focus_sum[s.subject] = focus_sum.get(s.subject, 0) + s.focus_rating
            focus_count[s.subject] = focus_count.get(s.subject, 0) + 1

        best_subject = max(
            focus_sum.keys(),
            key=lambda sub: focus_sum[sub] / focus_count[sub]
        )

    # -------- coach insights --------
    insights = []

    if not week_sessions:
        insights.append("Log your first study session to start getting insights.")
    else:
        if days_studied <= 2:
            insights.append("Try studying on 3+ days this week to build consistency.")
        elif days_studied >= 5:
            insights.append("Nice consistency — 5+ study days is a strong habit.")

        if avg_focus is not None:
            if avg_focus < 3:
                insights.append("Your focus is low on average. Try shorter sessions.")
            elif avg_focus >= 4:
                insights.append("Great focus this week — keep it up.")

        if minutes_this_week < 60:
            insights.append("You studied under 60 minutes this week. Even small daily sessions help.")
        elif minutes_this_week >= 300:
            insights.append("Big week (300+ minutes). Make sure to rest to stay consistent.")

        if best_subject:
            insights.append(f"Your best-focus subject this week was {best_subject}.")

    return render_template(
        "dashboard.html",
        sessions=sessions,
        tasks=tasks,
        sessions_count=sessions_count,
        tasks_count=tasks_count,
        minutes_this_week=minutes_this_week,
        days_studied=days_studied,
        avg_focus=avg_focus,
        subject_minutes=subject_minutes_sorted,
        insights=insights
    )


@main_bp.route("/sessions/new", methods=["POST"])
@login_required
def create_session():
    subject = request.form.get("subject", "").strip()
    duration = request.form.get("duration_minutes", "")
    focus = request.form.get("focus_rating", "")

    if not subject:
        flash("Subject is required.")
        return redirect(url_for("main.dashboard"))

    try:
        duration = int(duration)
        focus = int(focus)
    except ValueError:
        flash("Invalid input.")
        return redirect(url_for("main.dashboard"))

    session = StudySession(
        user_id=current_user.id,
        subject=subject,
        duration_minutes=duration,
        focus_rating=focus
    )
    db.session.add(session)
    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main_bp.route("/tasks/new", methods=["POST"])
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Task title required.")
        return redirect(url_for("main.dashboard"))

    task = Task(user_id=current_user.id, title=title)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("main.dashboard"))

@main_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.completed = not task.completed
        db.session.commit()
    return redirect(url_for("main.dashboard"))

@main_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("main.dashboard"))
