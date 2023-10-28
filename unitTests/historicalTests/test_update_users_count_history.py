import unittest
from unittest.mock import patch
from datetime import datetime
from historical_data import update_users_count_history


class TestUpdateUsersCountHistory(unittest.TestCase):
    @patch("historical_data.current_time")
    def test_update_users_count_history_first_time(self, mock_current_time):
        mock_current_time.strftime.return_value = "2023-10-10-10:00:00"
        all_users = {"user1": {"isOnline": True}, "user2": {"isOnline": False}}
        expected_result = {"2023-10-10-10:00:00": {"usersOnline": 1}}
        result = update_users_count_history(all_users)
        self.assertEqual(expected_result, result)

    @patch("historical_data.current_time")
    @patch("historical_data.last_updated_time", "2023-10-10-10:00:00")
    def test_update_users_count_history_not_first_time(self, mock_current_time):
        mock_current_time.strftime.return_value = "2023-10-10-10:00:05"
        all_users = {"user1": {"isOnline": True}, "user2": {"isOnline": False}, "user3": {"isOnline": True}, "user4": {"isOnline": True}}
        expected_result = {"2023-10-10-10:00:00": {"usersOnline": 1}, "2023-10-10-10:00:05": {"usersOnline": 3}}
        last_updated_time = datetime.strptime("2023-10-10-10:00:00", "%Y-%m-%d-%H:%M:%S")
        with patch("historical_data.last_updated_time", last_updated_time):
            result = update_users_count_history(all_users)
        self.assertEqual(expected_result, result)
