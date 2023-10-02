import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from main import process_user_data


class TestProcessUserData(unittest.TestCase):

    @patch('main.fetch_user_data')
    def test_process_user_data(self, mock_fetch_user_data):

        mock_response = {
            "data": [
                {"nickname": "user1", "isOnline": True, "lastSeenDate": None},
                {"nickname": "user2", "isOnline": False, "lastSeenDate": (datetime.utcnow() - timedelta(seconds=45)).isoformat()}
            ]
        }
        mock_fetch_user_data.return_value = mock_response
        all_users_data = {}

        process_user_data(mock_response, 0, all_users_data)

        expected_result = {
            "user1": mock_response["data"][0],
            "user2": mock_response["data"][1]
        }

        self.assertEqual(expected_result, all_users_data)
