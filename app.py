import csv
import io
import json
import os
from datetime import datetime

from flask import (Flask, render_template, request, Response,
                   redirect, url_for, flash, jsonify)
from flask_sqlalchemy import SQLAlchemy

from tasks import TASKS, TOTAL_TASKS

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

db_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------- Models ----------
class Participant(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(50), nullable=False)
    age            = db.Column(db.Integer, nullable=False)
    device         = db.Column(db.String(50), nullable=False)
    vision_group   = db.Column(db.String(50), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship("TaskResponse", backref="participant",
                                cascade="all, delete-orphan", lazy=True)


class TaskResponse(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey("participant.id"), nullable=False)
    task_number    = db.Column(db.Integer, nullable=False)
    task_name      = db.Column(db.String(100), nullable=False)
    response       = db.Column(db.String(2000))
    data           = db.Column(db.Text)          # JSON blob of rich data
    correct        = db.Column(db.Boolean)
    duration_ms    = db.Column(db.Integer)
    completed_at   = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pid  = (request.form.get("participantId") or "").strip()
        age  = (request.form.get("age") or "").strip()
        dev  = request.form.get("device", "Tablet")
        vg   = request.form.get("visionGroup", "Low vision")

        if not pid or not age:
            flash("Please fill in the Participant ID and Age.", "error")
            return redirect(url_for("index"))
        try:
            age_int = int(age)
        except ValueError:
            flash("Age must be a number.", "error")
            return redirect(url_for("index"))

        p = Participant(participant_id=pid, age=age_int, device=dev, vision_group=vg)
        db.session.add(p)
        db.session.commit()
        return redirect(url_for("assessment_task", participant_id=p.id, task_num=1))

    return render_template("index.html", total_tasks=TOTAL_TASKS)


@app.route("/assessment/<int:participant_id>/task/<int:task_num>")
def assessment_task(participant_id, task_num):
    participant = Participant.query.get_or_404(participant_id)
    if task_num > TOTAL_TASKS:
        return redirect(url_for("assessment_complete", participant_id=participant.id))
    if task_num < 1:
        return redirect(url_for("assessment_task", participant_id=participant.id, task_num=1))

    task = TASKS[task_num - 1]
    progress = int((task_num - 1) / TOTAL_TASKS * 100)
    return render_template("task.html",
                           participant=participant, task=task,
                           task_num=task_num, total=TOTAL_TASKS,
                           progress=progress)


@app.route("/api/submit_task", methods=["POST"])
def api_submit_task():
    payload = request.get_json() or {}
    participant_id = payload.get("participant_id")
    task_number    = payload.get("task_number")

    participant = Participant.query.get_or_404(participant_id)
    task = next((t for t in TASKS if t["n"] == task_number), None)
    if not task:
        return jsonify({"error": "unknown task"}), 400

    response_val = payload.get("response", "")
    rich_data    = payload.get("data", {})
    duration_ms  = payload.get("duration_ms")

    # Optional scoring: if task config has correct answer, compare
    correct = None
    cfg = task.get("config", {})
    if "number" in cfg and task["type"] == "ishihara":
        correct = str(response_val).strip() == cfg["number"]
    elif "text" in cfg and task["type"] in ("reading", "sign", "label"):
        correct = str(response_val).strip().lower() == cfg["text"].lower()
    elif "has_obstacle" in cfg and task["type"] == "obstacle":
        correct = (str(response_val).strip().lower() == "yes") == bool(cfg["has_obstacle"])

    rec = TaskResponse(
        participant_id=participant.id,
        task_number=task_number,
        task_name=task["name"],
        response=str(response_val)[:2000],
        data=json.dumps(rich_data)[:10000],
        correct=correct,
        duration_ms=duration_ms,
    )
    db.session.add(rec)
    db.session.commit()

    next_num = task_number + 1
    next_url = (url_for("assessment_complete", participant_id=participant.id)
                if next_num > TOTAL_TASKS else
                url_for("assessment_task", participant_id=participant.id, task_num=next_num))
    return jsonify({"ok": True, "next": next_url})


@app.route("/assessment/<int:participant_id>/complete")
def assessment_complete(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    responses = (TaskResponse.query
                 .filter_by(participant_id=participant.id)
                 .order_by(TaskResponse.task_number).all())
    scored = [r for r in responses if r.correct is not None]
    score = sum(1 for r in scored if r.correct)
    return render_template("complete.html",
                           participant=participant, responses=responses,
                           score=score, scored_total=len(scored))


# ---------- CSV Exports ----------
def _write_rows(writer, participants):
    writer.writerow(["Participant ID", "Age", "Device", "Vision Group",
                     "Task #", "Task Name", "Response", "Correct",
                     "Duration (ms)", "Details", "Timestamp"])
    for p in participants:
        for r in sorted(p.responses, key=lambda x: x.task_number):
            writer.writerow([
                p.participant_id, p.age, p.device, p.vision_group,
                r.task_number, r.task_name, r.response,
                "" if r.correct is None else ("1" if r.correct else "0"),
                r.duration_ms or "",
                r.data or "",
                r.completed_at.strftime("%Y-%m-%d %H:%M:%S") if r.completed_at else "",
            ])


@app.route("/export")
def export_csv():
    output = io.StringIO()
    w = csv.writer(output)
    _write_rows(w, Participant.query.order_by(Participant.created_at).all())
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=all_participants.csv"})


@app.route("/export/participant/<int:participant_id>")
def export_participant(participant_id):
    p = Participant.query.get_or_404(participant_id)
    output = io.StringIO()
    w = csv.writer(output)
    _write_rows(w, [p])
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":
                             f"attachment; filename=participant_{p.participant_id}.csv"})


@app.route("/export/wide")
def export_wide():
    """One row per participant, one column per task (easy for SPSS/R)."""
    output = io.StringIO()
    w = csv.writer(output)
    header = ["Participant ID", "Age", "Device", "Vision Group", "Date"]
    for t in TASKS:
        header += [f"T{t['n']}_Response", f"T{t['n']}_Correct", f"T{t['n']}_ms"]
    w.writerow(header)

    for p in Participant.query.order_by(Participant.created_at).all():
        row = [p.participant_id, p.age, p.device, p.vision_group,
               p.created_at.strftime("%Y-%m-%d %H:%M")]
        by_num = {r.task_number: r for r in p.responses}
        for t in TASKS:
            r = by_num.get(t["n"])
            if r:
                row += [r.response or "",
                        "" if r.correct is None else int(r.correct),
                        r.duration_ms or ""]
            else:
                row += ["", "", ""]
        w.writerow(row)

    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=wide_format.csv"})


@app.route("/health")
def health():
    return {"status": "ok", "tasks": TOTAL_TASKS}


if __name__ == "__main__":
    app.run(debug=True)