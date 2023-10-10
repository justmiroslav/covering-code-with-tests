import unittest
from unittest.mock import patch
from historical_data import get_user_info


class TestGetUserInfo(unittest.TestCase):

    @patch('historical_data.user_info_history', {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": "2023-10-10-10:00:00"}}})
    def test_get_user_info_valid_date_and_user_id(self):
        date = "2023-10-10-10:00:00"
        user_id = "user1"
        expected_result = {"wasUserOnline": True, "nearestOnlineTime": None}

        result = get_user_info(date, user_id)

        self.assertEqual(expected_result, result)

    @patch('historical_data.user_info_history', {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": None}}})
    def test_get_user_info_invalid_date(self):
        date = "2023-10-10-11:00:00"
        user_id = "user1"
        expected_result = "No information about this user at specified date"

        result = get_user_info(date, user_id)

        self.assertEqual(expected_result, result)

    @patch('historical_data.user_info_history', {"2023-10-10-10:00:00": {"user1": {"wasUserOnline": False, "nearestOnlineTime": "2023-10-10-09:30:00"}}})
    def test_get_user_info_user_was_not_online(self):
        date = "2023-10-10-10:00:00"
        user_id = "user1"
        expected_result = {"wasUserOnline": False, "nearestOnlineTime": "2023-10-10-09:30:00"}

        result = get_user_info(date, user_id)

        self.assertEqual(expected_result, result)
