import time
import threading
import re
from itertools import combinations
from fastapi import FastAPI, Query
from last_seen import *

app = FastAPI()
current_time = datetime.utcnow()
last_updated_time = current_time
userId_by_nickname = {}
users_count_history = {}
user_info_history = {}
template_reports = {}
reports = {}
forgotten_users = []
stop_event = threading.Event()


def format_result(number):
    if number.is_integer():
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
    while True:
        if stop_event.is_set():
            break
        users_data = load_user_data(last_seen_api_url)
        userId_by_nickname.clear()
        user_count = update_users_count_history(users_data)
        last_key = next(reversed(user_count))
        user_count_data = {f"{last_key}": dict(users_count_history[last_key])}
        user_info_data = {f"{last_key}": {}}

        for user, user_data in users_data.items():
            user_id = user_data["userId"]
            last_seen_date_str = user_data["lastSeenDate"]

            if user_data["userId"] not in forgotten_users:
                userId_by_nickname[user_data["nickname"]] = user_data["userId"]

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
    users_count_history.update(data)


@app.post("/api/update_info")
def update_info(data: dict):
    user_info_history.update(data)


@app.get("/api/stats/users")
def get_user_count(date: str = Query(...)):
    for key, value in users_count_history.items():
        if key == date:
            return {"usersOnline": value.get("usersOnline")}

    return {"usersOnline": None}


@app.get("/api/stats/user")
def get_user_info(date: str = Query(...), user_id: str = Query(...)):
    if date not in user_info_history:
        return "No information about this user at specified date"

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
def calculate_average_time(user_id: str = Query(...), from_date=None, to_date=None):
    total_time = 0
    daily_time = 0
    weekly_time = 0
    days = []
    weeks = []
    first_day = None
    day_day = None
    week_day = None
    last_day = None
    last_week = False
    last_day_day = False

    if from_date and to_date:
        from_cur_date = datetime.strptime(from_date, "%Y-%m-%d-%H:%M:%S")
        to_cur_date = datetime.strptime(to_date, "%Y-%m-%d-%H:%M:%S")
        for key, value in user_info_history.items():
            while from_cur_date <= datetime.strptime(key, "%Y-%m-%d-%H:%M:%S") <= to_cur_date:
                if user_id in value and value[user_id]["wasUserOnline"]:
                    total_time += 5
                    weekly_time += 5
                    if first_day is None:
                        first_day = key
                        day_day = key
                        week_day = key
                    last_day = key

                if (datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S") - datetime.strptime(day_day, "%Y-%m-%d-%H:%M:%S")).days >= 1:
                    if (datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S") - datetime.strptime(week_day, "%Y-%m-%d-%H:%M:%S")).days >= 6:
                        weeks.append(weekly_time)
                        week_day = last_day
                        weekly_time = 0
                        last_week = True
                    days.append(weekly_time)
                    day_day = last_day
                    daily_time = 0
                    last_day_day = True

                elif (datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S") - datetime.strptime(week_day, "%Y-%m-%d-%H:%M:%S")).days < 6 and last_week:
                    if (datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S") - datetime.strptime(day_day, "%Y-%m-%d-%H:%M:%S")).days < 1 and last_day_day:
                        days.append(daily_time)
                    weeks.append(weekly_time)

        daily_average = format_result(sum(days) / len(days))

        if weeks:
            weekly_average = format_result(sum(weeks) / len(weeks))
        else:
            weekly_average = format_result(daily_average * 7)

        return {"dailyAverage": daily_average, "weeklyAverage": weekly_average, "total": total_time, "min": min(days), "max": max(days)}

    else:
        for key, value in user_info_history.items():
            if user_id in value and value[user_id]["wasUserOnline"]:
                total_time += 5
                weekly_time += 5
            if first_day is None:
                first_day = key
                week_day = key
            last_day = key

            if (datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S") - datetime.strptime(week_day, "%Y-%m-%d-%H:%M:%S")).days >= 6:
                weeks.append(weekly_time)
                week_day = last_day
                weekly_time = 0
                last_week = True

            elif (datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S") - datetime.strptime(week_day, "%Y-%m-%d-%H:%M:%S")).days < 6 and last_week:
                weeks.append(weekly_time)

        first_date = datetime.strptime(first_day, "%Y-%m-%d-%H:%M:%S")
        last_date = datetime.strptime(last_day, "%Y-%m-%d-%H:%M:%S")
        day_difference = (last_date - first_date).days

        daily_average = format_result(total_time / (day_difference + 1))

        if weeks:
            weekly_average = format_result(sum(weeks) / len(weeks))
        else:
            weekly_average = format_result(daily_average * 7)

        return {"weeklyAverage": weekly_average, "dailyAverage": daily_average}


@app.post("/api/user/forget")
def forget_user(user_id: str = Query(...)):
    for key, value in userId_by_nickname.items():
        if user_id == value:
            del userId_by_nickname[key]

    for key, value in users_count_history.items():
        if user_id in value:
            del users_count_history[key][user_id]

    for key, value in user_info_history.items():
        if user_id in value:
            del user_info_history[key][user_id]

    forgotten_users.append(user_id)

    return "User data has been forgotten"


@app.post("/api/report")
def configure_report(report_name: str = Query(...)):
    if report_name not in template_reports.keys():
        return "Report not found"
    else:
        reports[report_name] = template_reports[report_name]
        return {}


@app.get("/api/report")
def get_report_data(report_name: str = Query(...), from_date: str = Query(...), to_date: str = Query(...)):
    if datetime.strptime(from_date, "%Y-%m-%d-%H:%M:%S") > datetime.strptime(to_date, "%Y-%m-%d-%H:%M:%S"):
        return "start date must be earlier than end date"
    if datetime.strptime(next(iter(user_info_history)), "%Y-%m-%d-%H:%M:%S") > datetime.strptime(from_date, "%Y-%m-%d-%H:%M:%S") or datetime.strptime(next(reversed(user_info_history)), "%Y-%m-%d-%H:%M:%S") < datetime.strptime(to_date, "%Y-%m-%d-%H:%M:%S"):
        return "specified date is not present in data dict"

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


def update_in_background():
    update_user_count_periodically()


if __name__ == "__main__":
    while True:
        bg_thread = threading.Thread(target=update_in_background)
        bg_thread.start()
        user_input = int(input("Enter 1 to print users online/2 to print info about specific user/3 to predict users online/4 to predict whether user is online/5 to calculate total online time\n"
                               "6 to calculate average online time/7 to cancel a user/8 to configure a report/9 to retrieve a report/10 to stop the program: "))
        if 1 <= user_input <= 4:
            print("Current time =", current_time.strftime("%Y-%m-%d-%H:%M:%S"))
            date_input = input("Enter the date: ")
            if user_input % 2 == 1:
                try:
                    if user_input == 1:
                        response = requests.get(f"http://localhost:8000/api/stats/users?date={date_input}")
                        print(response.json())
                    else:
                        response = requests.get(f"http://localhost:8000/api/predictions/users?date={date_input}")
                        print(response.json())
                except ValueError:
                    print("Enter a data in format YYYY-MM-DD-HH:MM:SS")
            elif user_input % 2 == 0:
                try:
                    while True:
                        username = input("Enter nickname of user you want to have info about: ")
                        if username not in userId_by_nickname.keys():
                            print("Enter a valid nickname")
                        else:
                            break
                    userId = userId_by_nickname[username]
                    if user_input == 2:
                        response = requests.get(f"http://localhost:8000/api/stats/user?date={date_input}&user_id={userId}")
                        print(response.json())
                    else:
                        pattern = r"^0\.?\d{1,2}$"
                        while True:
                            tolerance_rate = input("Enter tolerance rate: ")
                            if re.match(pattern, tolerance_rate) and 0.5 <= float(tolerance_rate) <= 0.99:
                                break
                            else:
                                print("Tolerance rate must be from 0.5 to 0.99")
                        response = requests.get(f"http://localhost:8000/api/predictions/user?date={date_input}&tolerance={float(tolerance_rate)}&user_id={userId}")
                        print(response.json())
                except ValueError:
                    print("Enter a data in format YYYY-MM-DD-HH:MM:SS")
        elif 5 <= user_input <= 7:
            while True:
                username = input("Enter nickname of user you want to have info about: ")
                if username not in userId_by_nickname.keys():
                    print("Enter a valid nickname")
                else:
                    break
            userId = userId_by_nickname[username]
            if user_input == 5:
                response = requests.get(f"http://localhost:8000/api/stats/user/total?user_id={userId}")
                print(response.json())
            elif user_input == 6:
                response = requests.get(f"http://localhost:8000/api/stats/user/average?user_id={userId}")
                print(response.json())
            else:
                response = requests.post(f"http://localhost:8000/api/user/forget?user_id={userId}")
                print(response.json())
        elif 8 <= user_input <= 9:
            available_metrics = ["dailyAverage", "weeklyAverage", "total", "min", "max"]
            for i in range(1, len(available_metrics) + 1):
                for metric_combination in combinations(available_metrics, i):
                    name_report = "_".join(metric_combination)
                    cur_report = {"metrics": list(metric_combination), "users": list(userId_by_nickname.values())}
                    template_reports[name_report] = cur_report
            if user_input == 8:
                while True:
                    report_input = input("Enter the report you want to have: ")
                    if report_input not in template_reports.keys():
                        print("Enter a valid report name")
                    else:
                        break
                response = requests.post(f"http://localhost:8000/api/report?report_name={report_input}")
                print(response.json())
            else:
                if not reports:
                    print("Before getting a report, you need to configure some of them")
                else:
                    while True:
                        report_input = input("Enter the report you want to have: ")
                        if report_input not in reports.keys():
                            print("Enter a valid report name")
                        else:
                            break
                    from_date_input = input("Enter a start date of your report")
                    to_date_input = input("Enter an end date of your report")
                    try:
                        response = requests.get(f"http://localhost:8000/api/report?report_name={report_input}&from_date={from_date_input}&to_date={to_date_input}")
                        print(response.json())
                    except ValueError:
                        print("Enter a data in format YYYY-MM-DD-HH:MM:SS")
        elif user_input == 10:
            stop_event.set()
            print("Waiting for background thread...")
            bg_thread.join()
            print("Stopped!")
            break
        else:
            print("Enter a valid command")
