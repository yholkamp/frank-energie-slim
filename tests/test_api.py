import unittest
from unittest.mock import patch
from datetime import datetime
from custom_components.frank_energie_slim.api import FrankEnergie

class TestFrankEnergie(unittest.TestCase):

    def setUp(self):
        # Patch the FrankEnergie class at the correct import location
        self.patcher = patch('custom_components.frank_energie_slim.api.FrankEnergie')
        self.MockFrankEnergie = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.MockFrankEnergie.return_value.auth = {'authToken': 'test_auth_token'}

    @patch('custom_components.frank_energie_slim.api.requests.post')
    def test_login_and_lookup(self, mock_post):
        # Placeholder JSON response for login
        mock_post.return_value.json.side_effect = [
            {
                "data": {
                    "login": {
                        "authToken": "test_auth_token",
                        "refreshToken": "test_refresh_token"
                    }
                }
            }
        ]

        # Initialize the API client
        client = FrankEnergie()

        # Test login
        auth = client.login("test_user", "test_password")
        self.assertEqual(auth['authToken'], "test_auth_token")
        self.assertEqual(auth['refreshToken'], "test_refresh_token")


    @patch('custom_components.frank_energie_slim.api.requests.post')
    def test_battery_and_session_lookup(self, mock_post):
        # Placeholder JSON response for battery lookup
        mock_post.return_value.json.side_effect = [
            {
                "data": {
                    "smartBatteries": [
                        {
                            "brand": "TestBrand",
                            "capacity": 100,
                            "createdAt": "2025-04-01T00:00:00Z",
                            "externalReference": "Ref123",
                            "id": "Battery1",
                            "maxChargePower": 50,
                            "maxDischargePower": 50,
                            "provider": "TestProvider",
                            "updatedAt": "2025-04-10T00:00:00Z"
                        }
                    ]
                }
            },
            {
                "data": {
                    "smartBatterySessions": {
                        "deviceId": "Battery1",
                        "periodStartDate": "2025-04-01",
                        "periodEndDate": "2025-04-10",
                        "periodEpexResult": 10.0,
                        "periodFrankSlim": 5.0,
                        "periodImbalanceResult": 2.0,
                        "periodTotalResult": 17.0,
                        "periodTradeIndex": 1.0,
                        "periodTradingResult": 3.0,
                        "sessions": [
                            {
                                "cumulativeTradingResult": 3.0,
                                "date": "2025-04-01",
                                "tradingResult": 3.0
                            }
                        ],
                        "totalTradingResult": 17.0
                    }
                }
            }
        ]

        # Initialize the API client
        client = FrankEnergie(auth_token="test_auth_token")
        client.auth = {'authToken': 'test_auth_token'}  # Ensure authToken is present

        # Test battery lookup
        batteries = client.get_smart_batteries()
        self.assertEqual(len(batteries['data']['smartBatteries']), 1)
        self.assertEqual(batteries['data']['smartBatteries'][0]['brand'], "TestBrand")

        # Test battery session lookup
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 10)
        sessions = client.get_smart_battery_sessions("Battery1", start_date, end_date)
        self.assertEqual(sessions['data']['smartBatterySessions']['deviceId'], "Battery1")
        self.assertEqual(sessions['data']['smartBatterySessions']['totalTradingResult'], 17.0)

if __name__ == "__main__":
    unittest.main()