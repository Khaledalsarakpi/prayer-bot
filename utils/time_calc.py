from datetime import datetime, timedelta


RAMADAN_START = datetime(2026, 2, 19)


def get_today_data(prayer_times_data):
    today = datetime.now().strftime("%Y-%m-%d")
    for day in prayer_times_data:
        if day.get("التاريخ_ميلادي") == today:
            return day
    return None


def get_ramadan_day():
    today = datetime.now()
    day = (today - RAMADAN_START).days + 1
    if 1 <= day <= 30:
        return day
    return None


def get_next_prayer(prayer_times_data):
    day_data = get_today_data(prayer_times_data)
    if not day_data:
        return None, None, None, None

    now = datetime.now()
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
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            seconds = remaining.seconds % 60
            return prayer, time, f"{hours:02d}:{minutes:02d}:{seconds:02d}", day_data.get("التاريخ_ميلادي")

    ramadan_day = get_ramadan_day() + 1 if get_ramadan_day() else 1
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    for day in prayer_times_data:
        if day.get("التاريخ_ميلادي") == tomorrow_str:
            return prayers[0][0], prayers[0][1].replace(" ص", "").replace("ص", ""), "غداً", tomorrow_str

    return prayers[0][0], prayers[0][1].replace(" ص", "").replace("ص", ""), "غداً", tomorrow_str


def format_remaining_time(remaining):
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    seconds = remaining.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
