import unittest
from unittest.mock import patch
from last_seen import load_user_data


class TestLoadUserData(unittest.TestCase):
    @patch("last_seen.fetch_user_data")
    def test_load_user_data(self, mock_fetch_user_data):
        mock_response_1 = {"data": [{"nickname": "user1", "isOnline": True, "lastSeenDate": None}]}
        mock_response_2 = {"data": []}
        mock_fetch_user_data.side_effect = [mock_response_1, mock_response_2]
        api_url = "https://example.com/api/users"
        result = load_user_data(api_url)
        expected_result = {
            "user1": mock_response_1["data"][0],
        }
        self.assertEqual(expected_result, result)
