# config.py

PROJECT_ID = "gothic-depth-474113-r1"
MODEL_NAME = "gemini-2.5-flash" # Or your preferred Gemini model
MAX_TURNS = 10 # Used for the outer loop, though we've fixed it to 5 cycles.
MAX_CORRECTION_ATTEMPTS = 3 # The number of times the intelligent analyst can try to fix its own code