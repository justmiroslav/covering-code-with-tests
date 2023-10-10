import requests
from dateutil import parser
from datetime import datetime, timedelta

current_time = datetime.utcnow()
last_seen_api_url = "https://sef.podkolzin.consulting/api/users/lastSeen"

translations = {
    "en": {
        "online": "is online",
        "was_online": "was online",
        "just_now": "just now",
        "less_than_a_minute_ago": "less than a minute ago",
        "a_couple_of_minutes_ago": "a couple of minutes ago",
        "an_hour_ago": "an hour ago",
        "today": "today",
        "yesterday": "yesterday",
        "this_week": "this week",
        "a_long_time_ago": "a long time ago"
    },
    "ua": {
        "online": "онлайн",
        "was_online": "був/була онлайн",
        "just_now": "щойно",
        "less_than_a_minute_ago": "менше хвилини тому",
        "a_couple_of_minutes_ago": "пару хвилин тому",
        "an_hour_ago": "годину тому",
        "today": "сьогодні",
        "yesterday": "вчора",
        "this_week": "цього тижня",
        "a_long_time_ago": "дуже давно"
    }
}


def fetch_user_data(api_url_1, offset_1):
    response = requests.get(f"{api_url_1}?offset={offset_1}")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def process_user_data(data_1, offset_1, all_users_data_1):
    for i, user_data_1 in enumerate(data_1["data"], start=offset_1 + 1):
        user_1 = f"user{i}"
        all_users_data_1[user_1] = user_data_1


def load_user_data(api_url_1):
    offset = 0
    all_users_data_1 = {}

    while True:
        data = fetch_user_data(api_url_1, offset)
        if data is not None:
            process_user_data(data, offset, all_users_data_1)
            if not data["data"]:
                break
            else:
                offset += len(data["data"])
        else:
            print("Failed to fetch data from the API.")
            break

    return all_users_data_1


def format_last_seen(l_s_str, cur_time, language):
    time_difference = cur_time - parser.isoparse(l_s_str).replace(tzinfo=None)

    if time_difference < timedelta(seconds=30):
        return translations[language]["just_now"]
    elif time_difference < timedelta(minutes=1):
        return translations[language]["less_than_a_minute_ago"]
    elif time_difference < timedelta(minutes=60):
        return translations[language]["a_couple_of_minutes_ago"]
    elif time_difference < timedelta(minutes=120):
        return translations[language]["an_hour_ago"]
    elif time_difference < timedelta(hours=24):
        return translations[language]["today"]
    elif time_difference < timedelta(days=2):
        return translations[language]["yesterday"]
    elif time_difference < timedelta(days=7):
        return translations[language]["this_week"]
    else:
        return translations[language]["a_long_time_ago"]


def print_user_data(all_users_data1, selected_language1):
    for user, user_data in all_users_data1.items():
        print(f"{user} = {user_data}")
        nickname = user_data["nickname"]
        is_online = user_data["isOnline"]
        last_seen_str = user_data["lastSeenDate"]

        if is_online:
            print(f"{nickname} {translations[selected_language1]['online']}.")
        else:
            last_seen = format_last_seen(last_seen_str, current_time, selected_language1)
            print(f"{nickname} {translations[selected_language1]['was_online']} {last_seen}.")


if __name__ == "__main__":
    while True:
        selected_language = input("en/ua: ").lower()
        if selected_language not in translations.keys():
            print(f"Selected language '{selected_language}' is not available. Enter another one")
        else:
            break
    print("Current time =", current_time.strftime("%Y-%m-%d-%H:%M:%S"))
    all_users_data = load_user_data(last_seen_api_url)
    print_user_data(all_users_data, selected_language)
