import json
from datetime import datetime, timedelta

def load_language(user_id):
    try:
        with open("docx/languages.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(user_id), "uk")
    except:
        return "uk"

def set_language(user_id, lang):
    try:
        with open("docx/languages.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}
    data[str(user_id)] = lang
    with open("docx/languages.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    with open("docx/admins.json", "r", encoding="utf-8") as f:
        admins = json.load(f)
    return user_id in admins

def get_faq_answer(lang, question):
    with open("docx/faq.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[lang].get(question, "⚠️ Вибачте, відповіді не знайдено.")

def get_court_info(lang):
    with open("docx/court_info.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[lang]

def get_available_dates():
    today = datetime.now().date()
    return [str(today + timedelta(days=i)) for i in range(14) if (today + timedelta(days=i)).weekday() < 5]

def get_available_times_for_date(selected_date):
    times = []
    for hour in range(9, 17):
        if hour == 13:
            continue
        times.append(f"{selected_date} {hour}:00")
    return times

def save_appointment(user_id, name, time):
    try:
        with open("docx/appointments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []
    data.append({"user_id": user_id, "name": name, "time": time})
    with open("docx/appointments.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_appointments_for_admin():
    try:
        with open("docx/appointments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return "Немає записів."
    return "\n".join([f"— {r['name']}, {r['time']}" for r in data])

def get_appointments_for_user():
    try:
        with open("docx/appointments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return "No appointments yet."
    return "\n".join([f"— {r['time']} ❌ Зайнято" for r in data])
