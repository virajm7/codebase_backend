import json
import os

STATE_FILE = "repo_state.json"


# =========================
# 🔥 SAFE SAVE (ATOMIC WRITE)
# =========================
def save_state(data):
    temp_file = STATE_FILE + ".tmp"

    try:
        with open(temp_file, "w") as f:
            json.dump(data, f)

        os.replace(temp_file, STATE_FILE)  # atomic replace
    except Exception as e:
        print("STATE SAVE ERROR:", e)


# =========================
# 🔥 SAFE LOAD (NO CRASH)
# =========================
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("STATE LOAD ERROR:", e)
        return {}