import requests


def process_user_data(data_dict):
    users_dict = {}
    for i, user_data_list in enumerate(data_dict["data"], start=1):
        user = f"user{i}"
        users_dict[user] = user_data_list
    return users_dict


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
            print(f"{nickname} is offline.")
else:
    print("Failed to fetch data from the API.")
