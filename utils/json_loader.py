import json
import os

DATA_FILE = "/root/prayer_bot/data/prayer_times.json"


def load_prayer_times():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def load_user_settings():
    settings_file = "/root/prayer_bot/data/user_settings.json"
    try:
        if os.path.exists(settings_file):
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}


def save_user_settings(settings):
    settings_file = "/root/prayer_bot/data/user_settings.json"
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
