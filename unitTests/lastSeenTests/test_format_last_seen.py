import unittest
from datetime import datetime, timedelta
from last_seen import format_last_seen, translations


class TestFormatLastSeen(unittest.TestCase):

    def setUp(self):
        self.current_time = datetime.utcnow()
        self.languages = ["ua", "en"]

    def test_format_last_seen_just_now(self):
        for language in self.languages:
            time = self.current_time - timedelta(seconds=15)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["just_now"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_less_than_a_minute_ago(self):
        for language in self.languages:
            time = self.current_time - timedelta(seconds=45)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["less_than_a_minute_ago"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_a_couple_of_minutes_ago(self):
        for language in self.languages:
            time = self.current_time - timedelta(minutes=45)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["a_couple_of_minutes_ago"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_an_hour_ago(self):
        for language in self.languages:
            time = self.current_time - timedelta(minutes=100)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["an_hour_ago"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_today(self):
        for language in self.languages:
            time = self.current_time - timedelta(hours=10)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["today"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_yesterday(self):
        for language in self.languages:
            time = self.current_time - timedelta(hours=35)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["yesterday"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_this_week(self):
        for language in self.languages:
            time = self.current_time - timedelta(days=5)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["this_week"]
            self.assertEqual(expected_translation, last_seen)

    def test_format_last_seen_a_long_time_ago(self):
        for language in self.languages:
            time = self.current_time - timedelta(days=100)
            last_seen = format_last_seen(time.isoformat(), self.current_time, language)
            expected_translation = translations[language]["a_long_time_ago"]
            self.assertEqual(expected_translation, last_seen)
