import unittest
from unittest.mock import patch
from historical_data import forget_user, users_count_history, user_info_history, user_Ids


class TestForgetUser(unittest.TestCase):
    @patch("historical_data.users_count_history", {"2023-10-13-12:00:00": {"user1": 5}})
    @patch("historical_data.user_info_history", {"2023-10-13-12:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": "2023-10-13-10:00:00"}}})
    def test_forget_user(self):
        user_id = "user1"
        response = forget_user(user_id)
        self.assertEqual(response, "User data has been forgotten")
        self.assertNotIn("user1", users_count_history)
        self.assertNotIn("user1", user_info_history)
        self.assertNotIn("user1", user_Ids)
