import unittest
from unittest.mock import patch
from historical_data import update_users_count_history


class TestUpdateUsersCountHistory(unittest.TestCase):
    @patch("historical_data.current_time")
    def test_update_users_count_history(self, mock_current_time):
        mock_current_time.strftime.return_value = "2023-10-10-10:00:00"
        all_users = {"user1": {"isOnline": True}, "user2": {"isOnline": False}}
        expected_result = {"2023-10-10-10:00:00": {"usersOnline": 1}}
        result = update_users_count_history(all_users)
        self.assertEqual(expected_result, result)
