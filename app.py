import csv
import io
from datetime import datetime
from flask import Flask, render_template, request, Response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here' # Needed for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    device = db.Column(db.String(50), nullable=False)
    vision_group = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables automatically
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        participant_id = request.form.get('participantId')
        age = request.form.get('age')
        device = request.form.get('device')
        vision_group = request.form.get('visionGroup')

        if not participant_id or not age:
            flash("Please fill in the Participant ID and Age.", "error")
            return redirect(url_for('index'))

        # Save to database
        new_participant = Participant(
            participant_id=participant_id,
            age=int(age),
            device=device,
            vision_group=vision_group
        )
        db.session.add(new_participant)
        db.session.commit()

        # In a real app, you would redirect to the first task here
        flash(f"Participant {participant_id} saved! Starting 18-Task Assessment...", "success")
        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/export')
def export_csv():
    # Fetch all participants from the database
    participants = Participant.query.all()

    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['ID', 'Participant ID', 'Age', 'Device', 'Vision Group', 'Date'])
    
    # Write data rows
    for p in participants:
        writer.writerow([p.id, p.participant_id, p.age, p.device, p.vision_group, p.created_at.strftime("%Y-%m-%d %H:%M:%S")])

    # Prepare the response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True)