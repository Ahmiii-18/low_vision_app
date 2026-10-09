"""
18-task Low Vision Functional Assessment protocol.
Each task defines: n, name, type, prompt, config.
The frontend renders an interactive stimulus based on `type`.
"""

TASKS = [
    {"n": 1, "name": "Distance Visual Acuity", "type": "snellen",
     "prompt": "Tap the direction the letter E is pointing.",
     "config": {"rounds": 6, "sizes": [220, 160, 110, 75, 50, 34]}},

    {"n": 2, "name": "Contrast Sensitivity", "type": "contrast",
     "prompt": "Is the letter visible? Tap YES or NO.",
     "config": {"letter": "H",
                "levels": [0.9, 0.7, 0.5, 0.35, 0.25, 0.15, 0.10, 0.06]}},

    {"n": 3, "name": "Color Vision (Ishihara)", "type": "ishihara",
     "prompt": "What number do you see in the circle?",
     "config": {"number": "74"}},

    {"n": 4, "name": "Amsler Grid", "type": "amsler",
     "prompt": "Stare at the center dot. Tap any areas where the lines look "
               "wavy, broken, or missing.",
     "config": {}},

    {"n": 5, "name": "Visual Field", "type": "visual_field",
     "prompt": "Keep your eyes on the center cross. Tap where the light appears.",
     "config": {"rounds": 8}},

    {"n": 6, "name": "Motion Detection", "type": "motion",
     "prompt": "Watch the dot. Which direction did it move?",
     "config": {"rounds": 5}},

    {"n": 7, "name": "Reading Speed", "type": "reading",
     "prompt": "Read the sentence aloud, then type it exactly.",
     "config": {"text": "The quick brown fox jumps over the lazy dog."}},

    {"n": 8, "name": "Glare Sensitivity", "type": "glare",
     "prompt": "Look at the light. Rate your discomfort "
               "(0 = none, 10 = unbearable).",
     "config": {}},

    {"n": 9, "name": "Face Recognition", "type": "face",
     "prompt": "What emotion does this face show?",
     "config": {"emotion": "happy",
                "options": ["Happy", "Sad", "Angry", "Surprised", "Neutral"]}},

    {"n": 10, "name": "Object Recognition", "type": "object",
     "prompt": "What object is shown?",
     "config": {"shape": "house",
                "options": ["House", "Tree", "Car", "Boat", "Star"]}},

    {"n": 11, "name": "Depth Perception", "type": "depth",
     "prompt": "Which circle appears closer to you?",
     "config": {"options": ["Left", "Right"]}},

    {"n": 12, "name": "Text Tracking", "type": "tracking",
     "prompt": "Watch the highlighted word. Type it when it stops.",
     "config": {}},

    {"n": 13, "name": "Sign Reading", "type": "sign",
     "prompt": "Read the sign aloud, then type the text you see.",
     "config": {"text": "STOP"}},

    {"n": 14, "name": "Medication Label", "type": "label",
     "prompt": "What dosage is on the label?",
     "config": {"text": "200 mg"}},

    {"n": 15, "name": "Obstacle Detection", "type": "obstacle",
     "prompt": "Is there an obstacle in the path?",
     "config": {"has_obstacle": True,
                "options": ["Yes", "No"]}},

    {"n": 16, "name": "Scene Recognition", "type": "scene",
     "prompt": "Describe what you see in one sentence.",
     "config": {}},

    {"n": 17, "name": "Peripheral Awareness", "type": "peripheral",
     "prompt": "Keep looking at the center dot. "
               "Which side did the shape appear on?",
     "config": {"rounds": 6}},

    {"n": 18, "name": "Daily Task Simulation", "type": "daily",
     "prompt": "Find and tap the bottle labeled 'Aspirin 100 mg'.",
     "config": {}},
]

TOTAL_TASKS = len(TASKS)