import unittest
from unittest.mock import patch
from historical_data import update_users_count_history


class TestUpdateUsersCountHistory(unittest.TestCase):
    def test_update_users_count_history(self):
        all_users = {"user1": {"isOnline": True}, "user2": {"isOnline": False}}
        with patch("historical_data.current_time") as mock_current_time:
            mock_current_time.strftime.return_value = "2023-10-10-10:00:00"
            users_count = update_users_count_history(all_users)
        self.assertEqual({"2023-10-10-10:00:00": {"usersOnline": 1}}, users_count)
