import unittest
from unittest.mock import patch
from historical_data import calculate_total_time


class TestCalculateTotalTime(unittest.TestCase):
    @patch('historical_data.user_info_history', {
        "2023-10-12-12:00:00": {"user1": {"wasUserOnline": True}},
        "2023-10-12-13:00:00": {"user1": {"wasUserOnline": False}},
        "2023-10-13-12:10:00": {"user1": {"wasUserOnline": True}}
    })
    def test_calculate_total_time(self):
        user_id = "user1"
        result = calculate_total_time(user_id)

        self.assertEqual({"totalTime": 10}, result)
