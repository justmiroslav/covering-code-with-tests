import unittest
from unittest.mock import patch
from historical_data import calculate_average_time


class TestCalculateAverageTime(unittest.TestCase):
    @patch('historical_data.user_info_history', {
        "2023-10-12-12:00:00": {"user1": {"wasUserOnline": True}},
        "2023-10-12-13:00:00": {"user1": {"wasUserOnline": False}},
        "2023-10-13-12:10:00": {"user1": {"wasUserOnline": True}},
        "2023-10-13-13:00:00": {"user1": {"wasUserOnline": True}},
        "2023-10-14-12:00:00": {"user1": {"wasUserOnline": True}},
    })
    def test_calculate_average_time_less_than_week(self):
        user_id = "user1"
        result = calculate_average_time(user_id)

        self.assertEqual({"weeklyAverage": 46.9, "dailyAverage": 6.7}, result)

    @patch('historical_data.user_info_history', {
        "2023-10-12-12:00:00": {"user1": {"wasUserOnline": True}},
        "2023-10-12-13:00:00": {"user1": {"wasUserOnline": False}},
        "2023-10-12-12:10:00": {"user1": {"wasUserOnline": False}},
        "2023-10-13-13:00:00": {"user1": {"wasUserOnline": True}},
        "2023-10-20-12:00:00": {"user1": {"wasUserOnline": True}},
        "2023-10-20-13:00:00": {"user1": {"wasUserOnline": True}},
    })
    def test_calculate_average_time_more_than_week(self):
        user_id = "user1"
        result = calculate_average_time(user_id)

        self.assertEqual({"weeklyAverage": 10, "dailyAverage": 2.2}, result)
