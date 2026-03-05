from datetime import datetime, timedelta
import json
import os
import pytz


SYRIA_TZ = pytz.timezone('Asia/Damascus')


def get_current_time():
    return datetime.now(SYRIA_TZ)


DATA_FILE = "/root/prayer_bot/data/prayer_times.json"
RAMADAN_START = datetime(2026, 2, 19, tzinfo=SYRIA_TZ)


def load_prayer_times():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def get_today_data():
    prayer_times_data = load_prayer_times()
    today = get_current_time().strftime("%Y-%m-%d")
    for day in prayer_times_data:
        if day.get("التاريخ_ميلادي") == today:
            return day
    return None


def get_ramadan_day():
    today = get_current_time()
    day = (today - RAMADAN_START).days + 1
    if 1 <= day <= 30:
        return day
    return None


def get_next_prayer():
    prayer_times_data = load_prayer_times()
    day_data = get_today_data()
    if not day_data:
        return None

    now = get_current_time()
    current_time = now.strftime("%H:%M")

    prayers = [
        ("الفجر", day_data.get("الفجر", "").replace(" ص", "").replace("ص", "")),
        ("الظهر", day_data.get("الظهر", "").replace(" م", "").replace("م", "")),
        ("العصر", day_data.get("العصر", "").replace(" م", "").replace("م", "")),
        ("المغرب", day_data.get("المغرب", "").replace(" م", "").replace("م", "")),
        ("العشاء", day_data.get("العشاء", "").replace(" م", "").replace("م", "")),
    ]

    for prayer, time in prayers:
        if time and time > current_time:
            target = datetime.strptime(time, "%H:%M")
            target = target.replace(year=now.year, month=now.month, day=now.day)
            remaining = target - now
            return {
                "prayer": prayer,
                "time": time,
                "remaining": remaining,
                "date": day_data.get("التاريخ_ميلادي"),
                "ramadan_day": day_data.get("اليوم_رمضان")
            }

    tomorrow = get_current_time() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    for day in prayer_times_data:
        if day.get("التاريخ_ميلادي") == tomorrow_str:
            return {
                "prayer": "الفجر",
                "time": day.get("الفجر", "").replace(" ص", "").replace("ص", ""),
                "remaining": None,
                "date": tomorrow_str,
                "ramadan_day": day.get("اليوم_رمضان"),
                "is_tomorrow": True
            }

    return None


def get_day_by_ramadan(day_num):
    prayer_times_data = load_prayer_times()
    for day in prayer_times_data:
        if day.get("اليوم_رمضان") == day_num:
            return day
    return None


def get_tomorrow_times():
    prayer_times_data = load_prayer_times()
    tomorrow = get_current_time() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    for day in prayer_times_data:
        if day.get("التاريخ_ميلادي") == tomorrow_str:
            return day
    return None
