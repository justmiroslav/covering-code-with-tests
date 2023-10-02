import unittest
from datetime import datetime, timedelta
from main import format_last_seen, translations, selected_language


class TestFormatLastSeen(unittest.TestCase):

    def setUp(self):
        self.current_time = datetime.utcnow()
        self.selected_language = selected_language

    def test_format_last_seen_just_now(self):
        time = self.current_time - timedelta(seconds=15)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["just_now"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_less_than_a_minute_ago(self):
        time = self.current_time - timedelta(seconds=45)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["less_than_a_minute_ago"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_a_couple_of_minutes_ago(self):
        time = self.current_time - timedelta(minutes=45)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["a_couple_of_minutes_ago"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_an_hour_ago(self):
        time = self.current_time - timedelta(minutes=100)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["an_hour_ago"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_today(self):
        time = self.current_time - timedelta(hours=10)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["today"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_yesterday(self):
        time = self.current_time - timedelta(hours=35)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["yesterday"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_this_week(self):
        time = self.current_time - timedelta(days=5)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["this_week"]
        self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_a_long_time_ago(self):
        time = self.current_time - timedelta(days=100)
        last_seen = format_last_seen(time.isoformat(), self.current_time, self.selected_language)
        expected_translation = translations[self.selected_language]["a_long_time_ago"]
        self.assertEqual(expected_translation, last_seen)
