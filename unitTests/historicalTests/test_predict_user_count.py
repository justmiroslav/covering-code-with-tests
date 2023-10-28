import unittest
from unittest.mock import patch
from historical_data import predict_user_count


class TestPredictUserCount(unittest.TestCase):
    @patch("historical_data.users_count_history", {"2023-10-10-10:00:00": {"usersOnline": 5}})
    def test_predict_user_count_valid_date(self):
        date = "2023-10-17-10:00:00"
        result = predict_user_count(date)
        self.assertEqual({"onlineUsers": 5}, result)

    @patch("historical_data.users_count_history", {"2023-10-10-10:00:00": {"usersOnline": 5}})
    def test_predict_user_count_invalid_date(self):
        date = "2023-10-16-10:00:00"
        result = predict_user_count(date)
        self.assertEqual({"onlineUsers": None}, result)
