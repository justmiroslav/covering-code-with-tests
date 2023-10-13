import unittest
import last_seen
import historical_data
from datetime import datetime


class TestSystem(unittest.TestCase):

    def test_load_user_data(self):
        all_users_data = last_seen.load_user_data(last_seen.last_seen_api_url)

        self.assertGreater(len(all_users_data), 0)
        for user, user_data in all_users_data.items():
            self.assertTrue(user.startswith("user"))
            self.assertIn("userId", user_data)
            self.assertIn("nickname", user_data)
            self.assertIn("isOnline", user_data)
            self.assertIn("lastSeenDate", user_data)

    def test_update_user_count_history(self):
        all_users_data = {
            "user1": {"userId": "1", "isOnline": True},
            "user2": {"userId": "2", "isOnline": False},
            "user3": {"userId": "3", "isOnline": True}
        }

        user_count_data = historical_data.update_users_count_history(all_users_data)

        self.assertEqual(1, len(user_count_data))
        last_updated_time = list(user_count_data.keys())[0]
        self.assertEqual(2, user_count_data[last_updated_time]["usersOnline"])

    def test_update_user_info_history(self):

        all_users_data = {
            "user1": {"userId": "1", "isOnline": True, "lastSeenDate": "2023-02-15T12:00:00Z"},
            "user2": {"userId": "2", "isOnline": False, "lastSeenDate": "2023-02-14T15:00:00Z"},
            "user3": {"userId": "3", "isOnline": True, "lastSeenDate": "2023-02-15T12:00:00Z"}
        }

        last_updated_time = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        user_info_data = {last_updated_time: {}}

        for user, user_data in all_users_data.items():
            user_id = user_data["userId"]
            user_info_data[last_updated_time][user_id] = {
                "wasUserOnline": user_data["isOnline"],
                "nearestOnlineTime": user_data["lastSeenDate"]
            }

        self.assertEqual(1, len(user_info_data))
        self.assertEqual(3, len(user_info_data[last_updated_time]))
        self.assertEqual(True, user_info_data[last_updated_time]["1"]["wasUserOnline"])
        self.assertEqual(False, user_info_data[last_updated_time]["2"]["wasUserOnline"])
        self.assertEqual(True, user_info_data[last_updated_time]["3"]["wasUserOnline"])
