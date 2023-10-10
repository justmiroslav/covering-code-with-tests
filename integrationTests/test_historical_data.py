import unittest
from fastapi.testclient import TestClient
from historical_data import app
from unittest.mock import Mock


class HistoricalDataIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_historical_data(self):
        mock_post = Mock()
        mock_get = Mock()

        self.client.post = mock_post
        self.client.get = mock_get

        user_count_data = {'2023-10-10-10:00:00': {'usersOnline': 5}}
        user_info_data = {'2023-10-10-10:00:00': {'user1': {'wasUserOnline': True}}}

        mock_post.return_value.status_code = 200
        mock_get.return_value.json.side_effect = [
            {'usersOnline': 5},
            {'wasUserOnline': True, 'nearestOnlineTime': None},
            {'onlineUsers': 5},
            {'willBeOnline': True, 'onlineChance': 1.0}
        ]

        self.client.post('/api/update_count', json=user_count_data)
        self.client.post('/api/update_info', json=user_info_data)

        response = self.client.get('/api/stats/users?date=2023-10-10-10:00:00')
        self.assertEqual(response.json(), {'usersOnline': 5})

        response = self.client.get('/api/stats/user?date=2023-10-10-10:00:00&user_id=user1')
        self.assertEqual(response.json(), {'wasUserOnline': True, 'nearestOnlineTime': None})

        response = self.client.get('/api/predictions/users?date=2023-10-17-10:00:00')
        self.assertEqual(response.json(), {'onlineUsers': 5})

        response = self.client.get('/api/predictions/user?date=2023-10-17-10:00:00&tolerance=0.5&user_id=user1')
        self.assertEqual(response.json(), {'willBeOnline': True, 'onlineChance': 1.0})
