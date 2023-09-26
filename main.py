import requests
from dateutil import parser
from datetime import datetime, timedelta


def process_user_data(data_dict):
    users_dict = {}
    for i, user_data_list in enumerate(data_dict["data"], start=1):
        user = f"user{i}"
        users_dict[user] = user_data_list
    return users_dict


def format_last_seen(l_s_str, cur_time):
    time_difference = cur_time - parser.isoparse(l_s_str).replace(tzinfo=None)

    if time_difference < timedelta(seconds=30):
        return "just now"
    elif time_difference < timedelta(minutes=1):
        return "less than a minute ago"
    elif time_difference < timedelta(minutes=60):
        return "a couple of minutes ago"
    elif time_difference < timedelta(minutes=120):
        return "an hour ago"
    elif time_difference < timedelta(hours=24):
        return "today"
    elif time_difference < timedelta(days=2):
        return "yesterday"
    elif time_difference < timedelta(days=7):
        return "this week"
    else:
        return "a long time ago"


current_time = datetime.utcnow()
print(current_time)
api_url = "https://sef.podkolzin.consulting/api/users/lastSeen?offset=20"
response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()
    users = process_user_data(data)
    for key, user_data in users.items():
        print(f"{key} = {user_data}")
        nickname = user_data["nickname"]
        is_online = user_data["isOnline"]
        last_seen_str = user_data["lastSeenDate"]

        if is_online:
            print(f"{nickname} is online.")
        else:
            last_seen = format_last_seen(last_seen_str, current_time)
            print(f"{nickname} was online {last_seen}.")
else:
    print("Failed to fetch data from the API.")
