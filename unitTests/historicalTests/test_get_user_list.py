import unittest
from unittest.mock import patch
from historical_data import get_user_list


class TestGetUserList(unittest.TestCase):
    @patch("historical_data.user_info_history", {"2023-01-01-00:00:00": {"user1": {"wasUserOnline": True}}})
    @patch("historical_data.username_dict", {"user1": "User1"})
    def test_get_user_list_with_online_user(self):
        expected_result = [{"username": "User1", "userId": "user1", "firstSeen": "2023-01-01-00:00:00"}]
        result = get_user_list()
        self.assertEqual(result, expected_result)

    @patch("historical_data.user_info_history", {"2023-01-01-00:00:00": {"user1": {"wasUserOnline": False}}})
    @patch("historical_data.username_dict", {"user1": "User1"})
    def test_get_user_list_with_offline_user(self):
        expected_result = [{"username": "User1", "userId": "user1", "firstSeen": "still offline"}]
        result = get_user_list()
        self.assertEqual(result, expected_result)

    @patch("historical_data.user_info_history", {"2023-01-01-00:00:00": {"user1": {"wasUserOnline": True}, "user2": {"wasUserOnline": False}}})
    @patch("historical_data.username_dict", {"user1": "User1", "user2": "User2"})
    def test_get_user_list_with_multiple_users(self):
        expected_result = [
            {"username": "User1", "userId": "user1", "firstSeen": "2023-01-01-00:00:00"},
            {"username": "User2", "userId": "user2", "firstSeen": "still offline"}]
        result = get_user_list()
        self.assertEqual(result, expected_result)
