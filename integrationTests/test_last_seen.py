import unittest
from unittest.mock import patch
from io import StringIO
import sys
from requests import Response
from last_seen import load_user_data, print_user_data


class LastSeenIntegrationTest(unittest.TestCase):
    @patch("requests.get")
    @patch("sys.stdout", new_callable=StringIO)
    def test_last_seen(self, mock_stdout, mock_get):
        mock_response_1 = Response()
        mock_response_1.status_code = 200
        mock_response_1.json = lambda: {
            "data": [
                {"nickname": "user1", "isOnline": True, "lastSeenDate": None},
                {"nickname": "user2", "isOnline": False, "lastSeenDate": "2023-01-01T10:00:00"}
            ]
        }
        mock_response_2 = Response()
        mock_response_2.status_code = 200
        mock_response_2.json = lambda: {"data": []}
        mock_get.side_effect = [mock_response_1, mock_response_2]
        try:
            all_users_data = load_user_data("https://example.com/api/users")
            print_user_data(all_users_data, "en")
        finally:
            sys.stdout = sys.__stdout__
        expected_output = "user1 = {'nickname': 'user1', 'isOnline': True, 'lastSeenDate': None}\n"
        expected_output += "user1 is online.\n"
        expected_output += "user2 = {'nickname': 'user2', 'isOnline': False, 'lastSeenDate': '2023-01-01T10:00:00'}\n"
        expected_output += "user2 was online a long time ago.\n"
        self.assertEqual(expected_output, mock_stdout.getvalue())
