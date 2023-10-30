import unittest
import last_seen
import historical_data
from datetime import datetime
from fastapi.testclient import TestClient
from historical_data import app


class TestSystem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_load_user_data(self):
        all_users_data = last_seen.load_user_data(last_seen.last_seen_api_url)
        self.assertGreater(len(all_users_data), 0)
        for user, user_data in all_users_data.items():
            self.assertTrue(user.startswith("user"))
            self.assertIn("userId", user_data)
            self.assertIn("nickname", user_data)
            self.assertIn("isOnline", user_data)
            self.assertIn("lastSeenDate", user_data)

    def test_update_user_count_history(self):
        all_users_data = {
            "user1": {"isOnline": True, "lastSeenDate": None},
            "user2": {"isOnline": True, "lastSeenDate": None}
        }
        user_count_data = historical_data.update_users_count_history(all_users_data)
        last_updated_time = list(user_count_data.keys())[0]
        self.assertEqual(2, user_count_data[last_updated_time]["usersOnline"])

    def test_update_user_info_history(self):
        all_users_data = {
            "user1": {"isOnline": True, "lastSeenDate": None},
            "user2": {"isOnline": True, "lastSeenDate": None}
        }
        last_updated_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        user_info_data = {last_updated_time: {}}
        for user, user_data in all_users_data.items():
            user_info_data[last_updated_time][user] = {
                "wasUserOnline": user_data["isOnline"],
                "nearestOnlineTime": user_data["lastSeenDate"]
            }
        self.assertEqual(True, user_info_data[last_updated_time]["user1"]["wasUserOnline"])
        self.assertEqual(True, user_info_data[last_updated_time]["user2"]["wasUserOnline"])

    def test_historical_data(self):
        user_count_data = {"2023-10-10-10:00:00": {"usersOnline": 2}, "2023-10-15-10:00:00": {"usersOnline": 1}}
        user_info_data = {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": True, "lastSeenDate": None}, "user2": {"wasUserOnline": True, "lastSeenDate": None}},
                          "2023-10-15-10:00:00": {"user1": {"wasUserOnline": False, "lastSeenDate": "2023-10-12-10:00:00", "user2": {"wasUserOnline": True, "lastSeenDate": None}}}}

        self.client.post("/api/update_count", json=user_count_data)
        self.client.post("/api/update_info", json=user_info_data)

        response = self.client.get("/api/stats/users?date=2023-10-10-10:00:00")
        self.assertEqual({"usersOnline": 2}, response.json())

        response = self.client.get("/api/stats/user?date=2023-10-10-10:00:00&user_id=user1")
        self.assertEqual({"wasUserOnline": True, "nearestOnlineTime": None}, response.json())

        response = self.client.get("/api/predictions/users?date=2023-10-17-10:00:00")
        self.assertEqual({"onlineUsers": 2}, response.json())

        response = self.client.get("/api/predictions/user?date=2023-10-17-10:00:00&tolerance=0.5&user_id=user1")
        self.assertEqual({"willBeOnline": True, "onlineChance": 1.0}, response.json())

        response = self.client.get("/api/stats/user/total?user_id=user1")
        self.assertEqual({"totalTime": 5}, response.json())

        response = self.client.get("/api/stats/user/average?user_id=user1")
        self.assertEqual({"weeklyAverage": 35, "dailyAverage": 5}, response.json())

        response = self.client.post("/api/user/forget?user_id=user2")
        self.assertEqual("User data has been forgotten", response.json())

        response = self.client.post(f"/api/report?report_name=dailyAverage")
        self.assertEqual({}, response.json())

        response = self.client.get("/api/report?report_name=dailyAverage&from_date=2023-10-10-10:00:00&to_date=2023-10-14-10:00:00")
        self.assertEqual([], response.json())
