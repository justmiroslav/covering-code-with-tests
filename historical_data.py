import time
import threading
from fastapi import FastAPI, Query
from last_seen import *

app = FastAPI()
current_time = datetime.utcnow()
last_updated_time = current_time
users_count_history = {}
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

        requests.post("http://localhost:8000/api/update_count", json=user_count_data)
        time.sleep(5)


@app.post("/api/update_count")
def update_count(data: dict):
    users_count_history.update(data)


@app.get("/api/stats/users")
def get_user_count(date: str = Query(...)):
    for key, value in users_count_history.items():
        if key == date:
            return {"usersOnline": value.get("usersOnline")}

    return {"usersOnline": None}


def update_in_background():
    update_user_count_periodically()


if __name__ == "__main__":
    while True:
        bg_thread = threading.Thread(target=update_in_background)
        bg_thread.start()
        another_input = int(input("Enter 1 to print users online/2 to stop the program: "))
        if 1 <= another_input <= 2:
            if another_input == 1:
                try:
                    print("Current time =", current_time.strftime("%Y-%m-%d-%H:%M:%S"))
                    date_input = input("Enter the date: ")
                    response = requests.get(f"http://localhost:8000/api/stats/users?date={date_input}")
                    print(response.json())
                except ValueError:
                    print("Enter a data in format YYYY-MM-DD-HH:MM:SS")
            elif another_input == 2:
                stop_event.set()
                print("Waiting for background thread...")
                bg_thread.join()
                print("Stopped!")
                break
        else:
            print("Enter a valid command")
