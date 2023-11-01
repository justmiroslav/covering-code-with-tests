import unittest
from unittest.mock import patch
from historical_data import get_reports_data


class TestGetReportsData(unittest.TestCase):
    @patch("historical_data.reports", {"report_name": {"metrics": ["dailyAverage", "weeklyAverage"], "users": ["user1", "user2"]}})
    def test_get_reports_data(self):
        result = get_reports_data()
        self.assertEqual([{"name": "report_name", "metrics": ["dailyAverage", "weeklyAverage"], "users": ["user1", "user2"]}], result)
