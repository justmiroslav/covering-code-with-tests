import unittest
from unittest.mock import patch
from historical_data import get_user_count


class TestGetUserCount(unittest.TestCase):

    @patch('historical_data.users_count_history', {"2023-10-10-10:00:00": {"usersOnline": 5}})
    def test_get_user_count_valid_date(self):
        date = "2023-10-10-10:00:00"
        expected_result = {"usersOnline": 5}

        result = get_user_count(date)

        self.assertEqual(expected_result, result)

    @patch('historical_data.users_count_history', {"2023-10-10-10:00:00": {"usersOnline": 5}})
    def test_get_user_count_invalid_date(self):
        date = "2023-10-10-11:00:00"
        expected_result = {"usersOnline": None}

        result = get_user_count(date)

        self.assertEqual(expected_result, result)
