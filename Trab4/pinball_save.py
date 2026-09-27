import json
from pathlib import Path


SAVE_FILE = Path(__file__).with_name("pinball_save.json")


def load_best_score():
    try:
        saved_data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0

    best = saved_data.get("best_score", 0) if isinstance(saved_data, dict) else 0
    return best if isinstance(best, int) and best >= 0 else 0


def save_best_score(best):
    try:
        SAVE_FILE.write_text(
            json.dumps({"best_score": best}, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass
