import csv
import io
import os
from datetime import datetime

from flask import (
    Flask, render_template, request, Response,
    redirect, url_for, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy

from tasks import TASKS, TOTAL_TASKS

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

db_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Participant(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(50), nullable=False)
    age            = db.Column(db.Integer, nullable=False)
    device         = db.Column(db.String(50), nullable=False)
    vision_group   = db.Column(db.String(50), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship(
        "TaskResponse", backref="participant",
        cascade="all, delete-orphan", lazy=True
    )


class TaskResponse(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    participant_id   = db.Column(db.Integer, db.ForeignKey("participant.id"), nullable=False)
    task_number      = db.Column(db.Integer, nullable=False)
    task_name        = db.Column(db.String(100), nullable=False)
    response         = db.Column(db.String(500))
    correct          = db.Column(db.Boolean, nullable=True)
    duration_ms      = db.Column(db.Integer, nullable=True)
    completed_at     = db.Column(db.DateTime, default=datetime.utcnow)


# Create tables on boot (idempotent)
with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        participant_id = (request.form.get("participantId") or "").strip()
        age            = (request.form.get("age") or "").strip()
        device         = request.form.get("device", "Tablet")
        vision_group   = request.form.get("visionGroup", "Low vision")

        if not participant_id or not age:
            flash("Please fill in the Participant ID and Age.", "error")
            return redirect(url_for("index"))

        try:
            age_int = int(age)
        except ValueError:
            flash("Age must be a number.", "error")
            return redirect(url_for("index"))

        p = Participant(
            participant_id=participant_id,
            age=age_int,
            device=device,
            vision_group=vision_group,
        )
        db.session.add(p)
        db.session.commit()

        return redirect(url_for("assessment_start", participant_id=p.id))

    return render_template("index.html", total_tasks=TOTAL_TASKS)


@app.route("/assessment/start/<int:participant_id>")
def assessment_start(participant_id):
    return redirect(url_for("assessment_task", participant_id=participant_id, task_num=1))


@app.route("/assessment/<int:participant_id>/task/<int:task_num>", methods=["GET", "POST"])
def assessment_task(participant_id, task_num):
    participant = Participant.query.get_or_404(participant_id)

    # Finished all tasks
    if task_num > TOTAL_TASKS:
        return redirect(url_for("assessment_complete", participant_id=participant.id))

    if task_num < 1:
        return redirect(url_for("assessment_start", participant_id=participant.id))

    task = TASKS[task_num - 1]

    if request.method == "POST":
        response_value = (request.form.get("response") or "").strip()
        duration_ms    = request.form.get("duration_ms")
        try:
            duration_int = int(duration_ms) if duration_ms else None
        except ValueError:
            duration_int = None

        correct = None
        if "correct" in task and task["correct"] is not None:
            correct = (response_value.lower() == str(task["correct"]).lower())

        record = TaskResponse(
            participant_id=participant.id,
            task_number=task_num,
            task_name=task["name"],
            response=response_value,
            correct=correct,
            duration_ms=duration_int,
        )
        db.session.add(record)
        db.session.commit()

        return redirect(url_for("assessment_task",
                                participant_id=participant.id,
                                task_num=task_num + 1))

    progress = int((task_num - 1) / TOTAL_TASKS * 100)
    return render_template(
        "task.html",
        participant=participant,
        task=task,
        task_num=task_num,
        total=TOTAL_TASKS,
        progress=progress,
    )


@app.route("/assessment/<int:participant_id>/complete")
def assessment_complete(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    responses = (TaskResponse.query
                 .filter_by(participant_id=participant.id)
                 .order_by(TaskResponse.task_number)
                 .all())

    scored = [r for r in responses if r.correct is not None]
    score = sum(1 for r in scored if r.correct)

    return render_template(
        "complete.html",
        participant=participant,
        responses=responses,
        score=score,
        scored_total=len(scored),
    )


@app.route("/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Participant ID", "Age", "Device", "Vision Group",
        "Task #", "Task Name", "Response", "Correct", "Duration (ms)", "Timestamp"
    ])

    participants = Participant.query.order_by(Participant.created_at).all()
    for p in participants:
        for r in sorted(p.responses, key=lambda x: x.task_number):
            writer.writerow([
                p.participant_id, p.age, p.device, p.vision_group,
                r.task_number, r.task_name, r.response,
                "" if r.correct is None else ("1" if r.correct else "0"),
                r.duration_ms or "",
                r.completed_at.strftime("%Y-%m-%d %H:%M:%S") if r.completed_at else "",
            ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=low_vision_data.csv"},
    )


@app.route("/api/tasks")
def api_tasks():
    """Optional: lets you inspect the task list as JSON."""
    return jsonify(TASKS)


@app.route("/health")
def health():
    return {"status": "ok", "tasks": TOTAL_TASKS}


if __name__ == "__main__":
    app.run(debug=True)