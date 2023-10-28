import unittest
from fastapi.testclient import TestClient
from historical_data import app
from unittest.mock import Mock


class HistoricalDataIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_historical_data(self):
        mock_post = Mock()
        mock_get = Mock()

        self.client.post = mock_post
        self.client.get = mock_get

        user_count_data = {"2023-10-10-10:00:00": {"usersOnline": 2}, "2023-10-15-10:00:00": {"usersOnline": 1}}
        user_info_data = {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": True, "lastSeenDate": None}, "user2": {"wasUserOnline": True, "lastSeenDate": None}},
                          "2023-10-15-10:00:00": {"user1": {"wasUserOnline": False, "lastSeenDate": "2023-10-12-10:00:00", "user2": {"wasUserOnline": True, "lastSeenDate": None}}}}

        mock_post.return_value.status_code = 200
        mock_get.return_value.json.side_effect = [
            {"usersOnline": 2},
            {"wasUserOnline": True, "nearestOnlineTime": None},
            {"onlineUsers": 2},
            {"willBeOnline": True, "onlineChance": 1.0},
            {"totalTime": 5},
            {"weeklyAverage": 5.6, "dailyAverage": 0.8},
            [{"userId": "user1", "metrics": [{"dailyAverage": 0.0, "weeklyAverage": 0.0}]},
             {"userId": "user2", "metrics": [{"dailyAverage": 0.0, "weeklyAverage": 0.0}]}]
        ]

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
        self.assertEqual({"weeklyAverage": 5.6, "dailyAverage": 0.8}, response.json())

        response = self.client.get("/api/report?report_name=custom_report&from_date=2023-10-10-10:00:00&to_date=2023-10-14-10:00:00")
        self.assertEqual([{"userId": "user1", "metrics": [{"dailyAverage": 0.0, "weeklyAverage": 0.0}]},
                          {"userId": "user2", "metrics": [{"dailyAverage": 0.0, "weeklyAverage": 0.0}]}], response.json())
