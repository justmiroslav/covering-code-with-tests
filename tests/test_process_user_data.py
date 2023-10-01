import unittest
from main import process_user_data


class TestProcessUserData(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            "data": [
                {
                    "nickname": "user1",
                    "isOnline": True,
                    "lastSeenDate": None
                },
                {
                    "nickname": "user2",
                    "isOnline": False,
                    "lastSeenDate": "2023-09-25T15:30:00Z"
                }
            ]
        }

    def test_process_user_data(self):
        all_users_data = {}
        process_user_data(self.sample_data, 0, all_users_data)
        expected_result = {
            "user1": self.sample_data["data"][0],
            "user2": self.sample_data["data"][1]
        }
        self.assertEqual(expected_result, all_users_data)
