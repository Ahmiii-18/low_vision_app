"""
Task definitions for the Low Vision Functional Assessment.

Each task is a dict with:
    n         : task number (1-18)
    name      : display name (short)
    prompt    : the instruction shown to the participant
    type      : "choice" | "text" | "number"
    options   : required only for type == "choice"
    correct   : optional. If set, the response is scored right/wrong.

Replace these placeholders with your approved protocol tasks.
"""

TASKS = [
    {"n": 1,  "name": "Distance Acuity", "prompt": "Read the letter on screen.", "type": "choice",
     "options": ["E", "F", "P", "T", "Z", "L"], "correct": "E"},

    {"n": 2,  "name": "Near Acuity", "prompt": "Type the smallest word you can read.", "type": "text"},

    {"n": 3,  "name": "Contrast Sensitivity", "prompt": "Is the letter visible?", "type": "choice",
     "options": ["Yes", "No"], "correct": "Yes"},

    {"n": 4,  "name": "Reading Speed", "prompt": "Type the sentence you just read.", "type": "text"},

    {"n": 5,  "name": "Central Field", "prompt": "Did you see a dot in the center?", "type": "choice",
     "options": ["Yes", "No"]},

    {"n": 6,  "name": "Peripheral Field", "prompt": "Which side did the light appear on?", "type": "choice",
     "options": ["Left", "Right", "Top", "Bottom"]},

    {"n": 7,  "name": "Color Vision", "prompt": "What number do you see?", "type": "text"},

    {"n": 8,  "name": "Glare Sensitivity", "prompt": "Rate discomfort from light (0-10).", "type": "number"},

    {"n": 9,  "name": "Face Recognition", "prompt": "Identify the emotion shown.", "type": "choice",
     "options": ["Happy", "Sad", "Angry", "Neutral", "Surprised"]},

    {"n": 10, "name": "Object Recognition", "prompt": "Name the object shown.", "type": "text"},

    {"n": 11, "name": "Motion Detection", "prompt": "Which direction did the shape move?", "type": "choice",
     "options": ["Left", "Right", "Up", "Down"]},

    {"n": 12, "name": "Depth Perception", "prompt": "Which object is closer?", "type": "choice",
     "options": ["Left", "Right"]},

    {"n": 13, "name": "Text Tracking", "prompt": "Type the word that was highlighted.", "type": "text"},

    {"n": 14, "name": "Sign Reading", "prompt": "Type the text on the sign.", "type": "text"},

    {"n": 15, "name": "Label Reading", "prompt": "What is the dosage on the label?", "type": "text"},

    {"n": 16, "name": "Obstacle Detection", "prompt": "Is there an obstacle in the path?", "type": "choice",
     "options": ["Yes", "No"]},

    {"n": 17, "name": "Scene Description", "prompt": "Describe the scene in one sentence.", "type": "text"},

    {"n": 18, "name": "Daily Task Simulation", "prompt": "Did you complete the task successfully?", "type": "choice",
     "options": ["Yes", "No"]},
]

TOTAL_TASKS = len(TASKS)