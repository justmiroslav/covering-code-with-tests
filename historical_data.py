import time
import threading
import re
from fastapi import FastAPI, Query
from last_seen import *

app = FastAPI()
current_time = datetime.utcnow()
last_updated_time = current_time
userId_by_nickname = {}
users_count_history = {}
user_info_history = {}
stop_event = threading.Event()


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
        user_count = update_users_count_history(users_data)
        last_key = next(reversed(user_count))
        user_count_data = {f"{last_key}": dict(users_count_history[last_key])}
        user_info_data = {f"{last_key}": {}}

        for user, user_data in users_data.items():
            user_id = user_data["userId"]
            nickname = user_data["nickname"]
            last_seen_date_str = user_data["lastSeenDate"]
            userId_by_nickname[nickname] = user_id
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
        return f"No information about this user at specified date"

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


def update_in_background():
    update_user_count_periodically()


if __name__ == "__main__":
    while True:
        bg_thread = threading.Thread(target=update_in_background)
        bg_thread.start()
        another_input = int(input("Enter 1 to print users online/2 to print info about specific user/3 to predict users online/4 to predict whether specific user will be online/5 to stop the program: "))
        if another_input == 5:
            stop_event.set()
            print("Waiting for background thread...")
            bg_thread.join()
            print("Stopped!")
            break
        elif 1 <= another_input <= 4:
            print("Current time =", current_time.strftime("%Y-%m-%d-%H:%M:%S"))
            date_input = input("Enter the date: ")
            if another_input % 2 == 1 and 1 <= another_input <= 3:
                try:
                    if another_input == 1:
                        response = requests.get(f"http://localhost:8000/api/stats/users?date={date_input}")
                        print(response.json())
                    else:
                        response = requests.get(f"http://localhost:8000/api/predictions/users?date={date_input}")
                        print(response.json())
                except ValueError:
                    print("Enter a data in format YYYY-MM-DD-HH:MM:SS")
            elif another_input % 2 == 0 and 2 <= another_input <= 4:
                try:
                    while True:
                        username = input("Enter nickname of user you want to have info about: ")
                        if username not in userId_by_nickname.keys():
                            print("Enter a valid nickname")
                        else:
                            break
                    userId = userId_by_nickname[username]
                    if another_input == 2:
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
        else:
            print("Enter a valid command")
