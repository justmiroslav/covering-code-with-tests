import unittest
from datetime import datetime
from main import process_user_data, format_last_seen


class TestMainFunctions(unittest.TestCase):

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
        self.current_time = datetime(2023, 9, 26, 12, 30, 0)

    def test_process_user_data(self):
        processed_data = process_user_data(self.sample_data)
        self.assertEqual({"user1": self.sample_data["data"][0], "user2": self.sample_data["data"][1]}, processed_data)

    def test_format_last_seen_just_now(self):
        last_seen = format_last_seen("2023-09-26T12:29:45Z", self.current_time)
        self.assertEqual("just now", last_seen)

    def test_format_last_seen_less_than_a_minute_ago(self):
        last_seen = format_last_seen("2023-09-26T12:29:15Z", self.current_time)
        self.assertEqual("less than a minute ago", last_seen)

    def test_format_last_seen_a_couple_of_minutes_ago(self):
        last_seen = format_last_seen("2023-09-26T11:31:00Z", self.current_time)
        self.assertEqual("a couple of minutes ago", last_seen)

    def test_format_last_seen_an_hour_ago(self):
        last_seen = format_last_seen("2023-09-26T11:00:00Z", self.current_time)
        self.assertEqual("an hour ago", last_seen)

    def test_format_last_seen_today(self):
        last_seen = format_last_seen("2023-09-26T07:00:00Z", self.current_time)
        self.assertEqual("today", last_seen)

    def test_format_last_seen_yesterday(self):
        last_seen = format_last_seen("2023-09-25T12:00:00Z", self.current_time)
        self.assertEqual("yesterday", last_seen)

    def test_format_last_seen_this_week(self):
        last_seen = format_last_seen("2023-09-22T12:00:00Z", self.current_time)
        self.assertEqual("this week", last_seen)

    def test_format_last_seen_a_long_time_ago(self):
        last_seen = format_last_seen("2023-08-01T12:00:00Z", self.current_time)
        self.assertEqual("a long time ago", last_seen)
