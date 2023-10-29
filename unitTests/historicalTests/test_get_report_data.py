import unittest
from unittest.mock import patch
from historical_data import get_report_data


class TestGetReportData(unittest.TestCase):
    @patch("historical_data.user_info_history", {"2023-01-01-00:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": "2023-01-01-15:00:00"}},
           "2023-01-01-15:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": None}},
           "2023-01-02-00:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": None}}})
    @patch("historical_data.reports", {"report_name": {"metrics": ["dailyAverage", "weeklyAverage"], "users": ["user1"]}})
    def test_get_report_data_success(self):
        report_name = "report_name"
        from_date = "2023-01-01-10:00:00"
        to_date = "2023-01-01-20:00:00"
        result = get_report_data(report_name, from_date, to_date)
        self.assertEqual([{"userId": "user1", "metrics": [{"dailyAverage": 5}, {"weeklyAverage": 35}]}], result)

    @patch("historical_data.user_info_history", {"2023-01-01-00:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": "2023-01-01-15:00:00"}},
           "2023-01-01-15:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": None}},
           "2023-01-02-00:00:00": {"user1": {"wasUserOnline": True, "nearestOnlineTime": None}}})
    @patch("historical_data.reports", {"report_name": {"metrics": ["dailyAverage", "weeklyAverage"], "users": ["user1"]}})
    def test_get_report_data_failure(self):
        report_name = "report_name"
        from_date = "2023-01-02-00:00:00"
        to_date = "2023-01-01-00:00:00"
        result = get_report_data(report_name, from_date, to_date)
        self.assertEqual("Start date must be earlier than end date", result)
