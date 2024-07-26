import json
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

hours = (9, 18)  # 9 AM to 6 PM
days_ahead = 5

def create_or_load_schedule():
    try:
        with open('schedule.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return generate_initial_schedule()

def get_today():
    return datetime.now()

def parse_date(relative_date):
    today = datetime.now()
    if relative_date.lower() == "today":
        return today.strftime('%Y-%m-%d')
    elif relative_date.lower() == "tomorrow":
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        try:
            return datetime.strptime(relative_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use 'today', 'tomorrow' or 'YYYY-MM-DD'.")

def generate_initial_schedule():
    schedule = {}
    today = datetime.now()
    for day in range(days_ahead):
        date = (today + timedelta(days=day)).strftime('%Y-%m-%d')
        schedule[date] = {f'{hour:02}:00': None for hour in range(hours[0], hours[1])}
        for _ in range(random.randint(3, 8)):
            hour = random.choice(list(schedule[date].keys()))
            schedule[date][hour] = {"name": fake.name(), "phone": fake.phone_number()}
    save_schedule(schedule)
    return schedule

def save_schedule(schedule):
    with open('schedule.json', 'w') as f:
        json.dump(schedule, f, indent=4)

def view_slots(date):
    schedule = create_or_load_schedule()
    available_slots = [time for time, name in schedule.get(date, {}).items() if name is None]
    return json.dumps({"date": date, "available_slots": available_slots})

def book_appointment(date, time, name, phone):
    schedule = create_or_load_schedule()
    if schedule.get(date, {}).get(time) is not None:
        return json.dumps({"error": f"Sorry, the slot at {time} on {date} is already booked!"})
    schedule.setdefault(date, {})[time] = {'name': name, 'phone': phone}
    save_schedule(schedule)
    return json.dumps({"success": f"Appointment booked for {name} ({phone}) at {time} on {date}."})

def submit_complaint(complaint, name):
    issues = []
    try:
        with open('issues.json', 'r') as f:
            issues = json.load(f)
    except FileNotFoundError:
        pass

    issues.append({'name': name, 'issue': complaint, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    with open('issues.json', 'w') as f:
        json.dump(issues, f, indent=4)

    return json.dumps({"success": "Issue submitted successfully."})

def cancel_appointment(name, phone):
    schedule = create_or_load_schedule()
    appointment_cancelled = False

    for date, times in schedule.items():
        for time, info in list(times.items()):
            if isinstance(info, dict) and info.get('name') == name and info.get('phone') == phone:
                schedule[date][time] = None
                appointment_cancelled = True
                break

    if appointment_cancelled:
        save_schedule(schedule)
        return json.dumps({"success": f"Appointment for {name} ({phone}) has been cancelled."})
    else:
        return json.dumps({"error": "No matching appointment found to cancel."})
