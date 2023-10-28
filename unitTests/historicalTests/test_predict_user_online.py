import unittest
from unittest.mock import patch
from historical_data import predict_user_online


class TestPredictUserOnline(unittest.TestCase):
    @patch("historical_data.user_info_history", {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": None}}})
    def test_predict_user_online_user_online(self):
        date = "2023-10-17-10:00:00"
        tolerance = 0.5
        user_id = "user1"
        result = predict_user_online(date, tolerance, user_id)
        self.assertEqual({"willBeOnline": True, "onlineChance": 1.0}, result)

    @patch("historical_data.user_info_history", {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": False, "nearestOnlineTime": "2023-10-10-09:30:00"}}})
    def test_predict_user_online_user_not_online(self):
        date = "2023-10-17-10:00:00"
        tolerance = 0.5
        user_id = "user1"
        result = predict_user_online(date, tolerance, user_id)
        self.assertEqual({"willBeOnline": False, "onlineChance": 0.0}, result)
