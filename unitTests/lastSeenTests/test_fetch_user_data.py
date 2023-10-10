import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from last_seen import fetch_user_data


class TestFetchUserData(unittest.TestCase):

    @patch('last_seen.requests.get')
    def test_fetch_user_data_success(self, mock_get):
        mock_response = {
            "data": [
                {"nickname": "user1", "isOnline": True, "lastSeenDate": None},
                {"nickname": "user2", "isOnline": False, "lastSeenDate": (datetime.utcnow() - timedelta(seconds=45)).isoformat()}
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        api_url = "https://example.com/api/users"
        offset = 0

        result = fetch_user_data(api_url, offset)

        self.assertEqual(mock_response, result)

    @patch('last_seen.requests.get')
    def test_fetch_user_data_failure(self, mock_get):
        mock_get.return_value.status_code = 404

        api_url = "https://example.com/api/users"
        offset = 0

        result = fetch_user_data(api_url, offset)

        self.assertIsNone(result)
