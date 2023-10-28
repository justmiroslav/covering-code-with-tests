import time
import threading
import re
from itertools import combinations
from fastapi import FastAPI, Query
from last_seen import *

app = FastAPI(title="Historical_Data")
last_updated_time = current_time
users_count_history = {}
user_info_history = {}
user_Ids = []
forgotten_users = []
template_reports = {}
reports = {}


def format_result(number):
    if number.is_integer():
        return number
    elif round(number, 1).is_integer():
        return int(number)
    else:
        return round(number, 1)


def update_users_count_history(all_users):
    global last_updated_time
    online_count = sum(1 for user_data in all_users.values() if user_data["isOnline"])
    cur_time = current_time.strftime("%Y-%m-%d-%H:%M:%S")

    if not users_count_history:
        users_count_history[cur_time] = {"usersOnline": online_count}
    else:
        last_updated_time += timedelta(seconds=5)
        cur_time = last_updated_time.strftime("%Y-%m-%d-%H:%M:%S")
        users_count_history[cur_time] = {"usersOnline": online_count}

    return users_count_history


def update_user_count_periodically():
    print(f"Sending data at {current_time.strftime('%Y-%m-%d-%H:%M:%S')}")
    while True:
        users_data = load_user_data(last_seen_api_url)
        user_count = update_users_count_history(users_data)
        last_key = next(reversed(user_count))
        user_count_data = {f"{last_key}": dict(users_count_history[last_key])}
        user_info_data = {f"{last_key}": {}}

        for user, user_data in users_data.items():
            user_id = user_data["userId"]
            last_seen_date_str = user_data["lastSeenDate"]
            if user_id not in forgotten_users:
                user_Ids.append(user_id)
                if user_id not in user_info_data[f"{last_key}"]:
                    if user_data["isOnline"]:
                        user_info_data[f"{last_key}"][user_id] = {
                            "wasUserOnline": user_data["isOnline"],
                            "nearestOnlineTime": last_seen_date_str}
                    else:
                        last_seen_date = parser.isoparse(last_seen_date_str).replace(tzinfo=None)
                        user_info_data[f"{last_key}"][user_id] = {
                            "wasUserOnline": user_data["isOnline"],
                            "nearestOnlineTime": last_seen_date.strftime("%Y-%m-%d-%H:%M:%S")}

        requests.post("http://localhost:8000/api/update_count", json=user_count_data)
        requests.post("http://localhost:8000/api/update_info", json=user_info_data)
        time.sleep(5)


@app.post("/api/update_count")
def update_count(data: dict):
    return users_count_history.update(data)


@app.post("/api/update_info")
def update_info(data: dict):
    return user_info_history.update(data)


@app.post("/api/user/forget")
def forget_user(user_id: str = Query(...)):
    forgotten_users.append(user_id)
    for key, value in users_count_history.items():
        if user_id in value:
            del users_count_history[key][user_id]
    for key, value in user_info_history.items():
        if user_id in value:
            del user_info_history[key][user_id]
    return "User data has been forgotten"


@app.post("/api/report")
def configure_report(report_name: str = Query(...)):
    available_metrics = ["dailyAverage", "weeklyAverage", "total", "min", "max"]
    for i in range(1, len(available_metrics) + 1):
        for metric_combination in combinations(available_metrics, i):
            name_report = "_".join(metric_combination)
            cur_report = {"metrics": list(metric_combination), "users": user_Ids}
            template_reports[name_report] = cur_report
    if report_name not in template_reports.keys():
        return "Report not found"
    reports[report_name] = template_reports[report_name]
    return {}


@app.get("/api/stats/users")
def get_user_count(date: str = Query(...)):
    for key, value in users_count_history.items():
        if key == date:
            return {"usersOnline": value.get("usersOnline")}
    return {"usersOnline": None}


@app.get("/api/stats/user")
def get_user_info(date: str = Query(...), user_id: str = Query(...)):
    date_time = datetime.strptime(date, "%Y-%m-%d-%H:%M:%S")
    was_user_online = False
    nearest_online_time = None
    for key, value in user_info_history.items():
        history_date = datetime.strptime(key, "%Y-%m-%d-%H:%M:%S")
        if history_date == date_time:
            if value.get(user_id) and value[user_id]["wasUserOnline"]:
                was_user_online = True
                nearest_online_time = history_date.strftime("%Y-%m-%d-%H:%M:%S")
        else:
            if was_user_online:
                continue
            if value.get(user_id) and value[user_id]["wasUserOnline"]:
                if not nearest_online_time:
                    nearest_online_time = history_date.strftime("%Y-%m-%d-%H:%M:%S")
                else:
                    current_delta = abs(history_date - date_time)
                    nearest_delta = abs(datetime.strptime(nearest_online_time, "%Y-%m-%d-%H:%M:%S") - date_time)
                    if current_delta < nearest_delta:
                        nearest_online_time = history_date.strftime("%Y-%m-%d-%H:%M:%S")
    if not was_user_online:
        if nearest_online_time is not None:
            return {"wasUserOnline": False, "nearestOnlineTime": nearest_online_time}
        else:
            return {"wasUserOnline": False, "nearestOnlineTime": user_info_history[date][user_id]["nearestOnlineTime"]}
    else:
        return {"wasUserOnline": True, "nearestOnlineTime": None}


@app.get("/api/predictions/users")
def predict_user_count(date: str = Query(...)):
    input_date = datetime.strptime(date, "%Y-%m-%d-%H:%M:%S")
    input_weekday = input_date.strftime("%A")
    matching_dates = []
    for key, value in users_count_history.items():
        history_date = datetime.strptime(key, "%Y-%m-%d-%H:%M:%S")
        weekday = history_date.strftime("%A")
        if weekday == input_weekday and history_date.time() == input_date.time():
            matching_dates.append(value["usersOnline"])
    if not matching_dates:
        return {"onlineUsers": None}
    else:
        return {"onlineUsers": sum(matching_dates) // len(matching_dates)}


@app.get("/api/predictions/user")
def predict_user_online(date: str = Query(...), tolerance: float = Query(...), user_id: str = Query(...)):
    pattern = r"^0\.?\d{1,2}$"
    if not (re.match(pattern, str(tolerance)) and 0.5 <= tolerance <= 0.99):
        return "Invalid tolerance rate"
    input_date = datetime.strptime(date, "%Y-%m-%d-%H:%M:%S")
    input_weekday = input_date.strftime("%A")
    matching_count = 0
    total_weeks = 0
    for key, value in user_info_history.items():
        history_date = datetime.strptime(key, "%Y-%m-%d-%H:%M:%S")
        weekday = history_date.strftime("%A")
        if weekday == input_weekday and history_date.time() == input_date.time():
            total_weeks += 1
            if value.get(user_id) and value[user_id]["wasUserOnline"]:
                matching_count += 1
    chance = matching_count / total_weeks
    if chance >= tolerance:
        return {"willBeOnline": True, "onlineChance": chance}
    else:
        return {"willBeOnline": False, "onlineChance": chance}


@app.get("/api/stats/user/total")
def calculate_total_time(user_id: str = Query(...)):
    total_time = 0
    for key, value in user_info_history.items():
        if user_id in value and value[user_id]["wasUserOnline"]:
            total_time += 5

    return {"totalTime": total_time}


@app.get("/api/stats/user/average")
def calculate_average_time(user_id: str = Query(...), from_date: str = None, to_date: str = None):
    total_time = 0
    daily_time = 0
    days = []
    if from_date and to_date:
        from_cur_date = datetime.strptime(from_date, "%Y-%m-%d-%H:%M:%S")
        to_cur_date = datetime.strptime(to_date, "%Y-%m-%d-%H:%M:%S")
        for key, value in user_info_history.items():
            date = datetime.strptime(key, "%Y-%m-%d-%H:%M:%S")
            if from_cur_date <= date <= to_cur_date and user_id in value and value[user_id]["wasUserOnline"]:
                daily_time += 5
            if date.day != (date - timedelta(days=1)).day:
                days.append(daily_time)
                daily_time = 0
        daily_average = format_result(sum(days) / len(days))
        weekly_average = format_result(daily_average * 7)
        return {"dailyAverage": daily_average, "weeklyAverage": weekly_average, "total": total_time, "min": min(days),
                "max": max(days)}
    else:
        for key, value in user_info_history.items():
            date = datetime.strptime(key, "%Y-%m-%d-%H:%M:%S")
            if user_id in value and value[user_id]["wasUserOnline"]:
                daily_time += 5
            if date.day != (date - timedelta(days=1)).day:
                days.append(daily_time)
                daily_time = 0
        daily_average = format_result(sum(days) / len(days))
        weekly_average = format_result(daily_average * 7)
        return {"weeklyAverage": weekly_average, "dailyAverage": daily_average}


@app.get("/api/report")
def get_report_data(report_name: str = Query(...), from_date: str = Query(...), to_date: str = Query(...)):
    if report_name not in reports:
        return "Report not found"
    if datetime.strptime(from_date, "%Y-%m-%d-%H:%M:%S") > datetime.strptime(to_date, "%Y-%m-%d-%H:%M:%S"):
        return "Start date must be earlier than end date"
    report_metrics = reports[report_name]["metrics"]
    result = []
    for user_id in reports[report_name]["users"]:
        user_data = {"userId": user_id, "metrics": []}
        metrics = calculate_average_time(user_id, from_date, to_date)
        for metric in report_metrics:
            if metric == "dailyAverage":
                user_data["metrics"].append({metric: metrics["dailyAverage"]})
            elif metric == "weeklyAverage":
                user_data["metrics"].append({metric: metrics["weeklyAverage"]})
            elif metric == "total":
                user_data["metrics"].append({metric: metrics["total"]})
            elif metric == "min":
                user_data["metrics"].append({metric: metrics["min"]})
            elif metric == "max":
                user_data["metrics"].append({metric: metrics["max"]})
        result.append(user_data)
    return result


update_thread = threading.Thread(target=update_user_count_periodically)
update_thread.start()
