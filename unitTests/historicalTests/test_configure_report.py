import unittest
from unittest.mock import patch
from historical_data import configure_report


class TestConfigureReport(unittest.TestCase):
    @patch("historical_data.template_reports", {"report_name": {"metrics": ["dailyAverage", "weeklyAverage"], "users": ["user1"]}})
    def test_configure_report_success(self):
        report_name = "report_name"
        result = configure_report(report_name)
        self.assertEqual(result, {})

    @patch("historical_data.template_reports", {"report_name": {"metrics": ["dailyAverage", "weeklyAverage"], "users": ["user1"]}})
    def test_configure_report_failure(self):
        report_name = "report_no_name"
        result = configure_report(report_name)
        self.assertEqual(result, "Report not found")
