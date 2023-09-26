import requests

api_url = "https://sef.podkolzin.consulting/api/users/lastSeen?offset=20"
response = requests.get(api_url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Failed to fetch data from the API.")
