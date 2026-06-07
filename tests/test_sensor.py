import unittest
from unittest.mock import patch, MagicMock, call
from custom_components.frank_energie_slim.sensor import FrankEnergieBatterySessionResultSensor, get_battery_mode_from_settings, augment_session
from custom_components.frank_energie_slim.api import FrankEnergie
from custom_components.frank_energie_slim.entities import (
    FrankEnergieBatterySessionResultSensor,
    FrankEnergieBatteryModeSensor,
    FrankEnergieBatteryStateOfChargeSensor,
    FrankEnergieTotalResultSensor,
    FrankEnergieTotalAvgSocSensor,
    FrankEnergieTotalLastModeSensor,
)
from custom_components.frank_energie_slim.api import FrankEnergie

class TestFrankEnergieBatterySessionResultSensor(unittest.TestCase):
    @patch('custom_components.frank_energie_slim.api.requests.post')
    def test_battery_session_result_sensors(self, mock_post):
        # Load mock session data as would be returned by the API
        session = augment_session({
            "deviceId": "id123",
            "periodStartDate": "2025-04-18",
            "periodEndDate": "2025-04-18",
            "periodBreakdownEpexCorrection": -0.10908,
            "periodBreakdownFrankSlim": 0.05807999999999999,
            "periodBreakdownTradingResult": 0.24638372,
            "periodResult": 0.19538371999999998,
            "sessions": [
                {"cumulativeResult": 22.07177538677404, "date": "2025-04-17", "result": 0.18},
                {"cumulativeResult": 22.31815910677404, "date": "2025-04-18", "result": 0.24638372},
            ],
        })
        # Brutoresultaat is derived: tradingResult + frankSlim
        expected_gross = 0.24638372 + 0.05807999999999999
        # totalTradingResult is derived from the latest session's running
        # cumulativeResult so the legacy `trading_result` entity ids keep working.
        self.assertEqual(session['totalTradingResult'], 22.31815910677404)
        # Test each result sensor
        sensors = [
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodBreakdownEpexCorrection', 'epex'), -0.10908, 'EPEX-correctie vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodBreakdownFrankSlim', 'frankslim'), 0.05807999999999999, 'Frank Slim vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodBreakdownTradingResult', 'handelsresultaat'), 0.24638372, 'Handelsresultaat vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodGrossResult', 'brutoresultaat'), expected_gross, 'Brutoresultaat vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodResult', 'nettoresultaat'), 0.19538371999999998, 'Totaalresultaat vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'totalTradingResult', 'trading_result'), 22.31815910677404, 'Handelsresultaat totaal'),
        ]
        for sensor, expected_state, expected_name in sensors:
            self.assertEqual(sensor.state, expected_state)
            self.assertEqual(sensor._attr_name, expected_name)

class TestFrankEnergieEntities(unittest.TestCase):
    def setUp(self):
        self.session = augment_session({
            "deviceId": "id123",
            "periodStartDate": "2025-04-18",
            "periodEndDate": "2025-04-18",
            "periodBreakdownEpexCorrection": -0.10908,
            "periodBreakdownFrankSlim": 0.05808,
            "periodBreakdownTradingResult": 0.24638,
            "periodResult": 0.19538,
        })
        self.details = {
            "smartBattery": {"brand": "SolarEdge", "provider": "SOLAREDGE", "settings": {"batteryMode": "auto"}},
            "smartBatterySummary": {"lastKnownStateOfCharge": 77}
        }

    def test_battery_mode_sensor(self):
        sensor = FrankEnergieBatteryModeSensor(None, "id123", "auto", self.details)
        self.assertEqual(sensor.state, "auto")
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "Batterijmodus")

    def test_battery_soc_sensor(self):
        sensor = FrankEnergieBatteryStateOfChargeSensor(None, "id123", 77, self.details)
        self.assertEqual(sensor.state, 77)
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "State of Charge")
        self.assertEqual(sensor._attr_unit_of_measurement, "%")

    def test_battery_session_result_sensor(self):
        sensor = FrankEnergieBatterySessionResultSensor(None, self.session, 'periodBreakdownEpexCorrection', 'epex', self.details)
        self.assertEqual(sensor.state, -0.10908)
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "EPEX-correctie vandaag")
        self.assertEqual(sensor._attr_unit_of_measurement, "EUR")

    def test_total_result_sensor(self):
        sensor = FrankEnergieTotalResultSensor(None, 'periodBreakdownEpexCorrection')
        self.assertEqual(sensor._attr_name, "EPEX-correctie vandaag")
        self.assertEqual(sensor._attr_unit_of_measurement, "EUR")
        self.assertEqual(sensor.device_info["name"], "Totaal batterijen")
        self.assertIsNone(sensor.state)

    def test_total_avg_soc_sensor(self):
        sensor = FrankEnergieTotalAvgSocSensor(None)
        sensor._state = 55.5
        self.assertEqual(sensor.state, 55.5)
        self.assertEqual(sensor._attr_name, "Gemiddelde SoC")
        self.assertEqual(sensor.device_info["name"], "Totaal batterijen")
        self.assertEqual(sensor._attr_unit_of_measurement, "%")

    def test_total_last_mode_sensor(self):
        sensor = FrankEnergieTotalLastModeSensor(None)
        sensor._state = "auto"
        self.assertEqual(sensor.state, "auto")
        self.assertEqual(sensor._attr_name, "Batterijmodus")
        self.assertEqual(sensor.device_info["name"], "Totaal batterijen")

class TestBatteryModeHelper(unittest.TestCase):
    def test_imbalance_aggressive(self):
        settings = {
            'batteryMode': 'IMBALANCE_TRADING',
            'imbalanceTradingStrategy': 'AGGRESSIVE',
            'selfConsumptionTradingThresholdPrice': None
        }
        self.assertEqual(get_battery_mode_from_settings(settings), 'imbalance_aggressive')

    def test_imbalance_non_aggressive(self):
        settings = {
            'batteryMode': 'IMBALANCE_TRADING',
            'imbalanceTradingStrategy': 'CONSERVATIVE',
            'selfConsumptionTradingThresholdPrice': None
        }
        self.assertEqual(get_battery_mode_from_settings(settings), 'imbalance')

    def test_self_consumption_plus(self):
        settings = {
            'batteryMode': 'SOMETHING_ELSE',
            'imbalanceTradingStrategy': 'AGGRESSIVE',
            'selfConsumptionTradingThresholdPrice': 0.05
        }
        self.assertEqual(get_battery_mode_from_settings(settings), 'self_consumption_plus')

    def test_self_consumption_zero_threshold(self):
        # A threshold of 0 is still a configured value (not None) → enabled
        settings = {
            'batteryMode': 'SOMETHING_ELSE',
            'imbalanceTradingStrategy': 'AGGRESSIVE',
            'selfConsumptionTradingThresholdPrice': 0
        }
        self.assertEqual(get_battery_mode_from_settings(settings), 'self_consumption_plus')

    def test_fallback(self):
        settings = {
            'batteryMode': 'SOMETHING_ELSE',
            'imbalanceTradingStrategy': 'AGGRESSIVE',
            'selfConsumptionTradingThresholdPrice': None
        }
        self.assertEqual(get_battery_mode_from_settings(settings), 'something_else')

class TestReAuthentication(unittest.TestCase):
    @patch('custom_components.frank_energie_slim.api.requests.post')
    async def test_authentication_required_exception_handling(self, mock_post):
        """Test that when an Authentication required exception is raised, the system re-authenticates."""
        # Create mock HomeAssistant
        hass = MagicMock()

        # Create mock client
        client = FrankEnergie()

        # Setup hass.data with our test client and credentials
        test_username = "test_user"
        test_password = "test_password"
        entry_id = "test_entry_id"
        hass.data = {
            "frank_energie_slim": {
                entry_id: {
                    "client": client,
                    "battery_ids": ["battery1"],
                    "username": test_username,
                    "password": test_password,
                    "battery_details": [{"smartBattery": {}, "smartBatterySummary": {}}]
                }
            }
        }

        # Setup mock responses
        # First call raises Authentication required exception
        def side_effect(*args, **kwargs):
            if mock_post.call_count == 1:
                response = MagicMock()
                response.json.return_value = {
                    "errors": [{"message": "user-error:auth-not-authorised"}]
                }
                return response
            else:
                response = MagicMock()
                response.json.return_value = {
                    "data": {
                        "login": {
                            "authToken": "new_auth_token",
                            "refreshToken": "new_refresh_token"
                        }
                    }
                }
                return response

        mock_post.side_effect = side_effect

        # Mock async_add_executor_job to simulate the API calls
        async def async_add_executor_job(func, *args, **kwargs):
            if func == client.get_smart_battery_sessions:
                if client.auth and 'authToken' in client.auth:
                    return {
                        "data": {
                            "smartBatterySessions": {
                                "deviceId": args[0],
                                "periodStartDate": "2025-04-01",
                                "periodEndDate": "2025-04-10",
                                "periodResult": 17.0,
                                "periodBreakdownEpexCorrection": 10.0,
                                "periodBreakdownFrankSlim": 5.0,
                                "periodBreakdownTradingResult": 2.0,
                                "sessions": []
                            }
                        }
                    }
                else:
                    raise Exception("Authentication required")
            elif func == client.login:
                client.auth = {"authToken": "new_auth_token", "refreshToken": "new_refresh_token"}
                return client.auth
            elif func == client.get_smart_battery_details:
                return {
                    "data": {
                        "smartBattery": {
                            "settings": {}
                        },
                        "smartBatterySummary": {}
                    }
                }
            return None

        hass.async_add_executor_job.side_effect = async_add_executor_job

        # Import the function here to avoid circular imports
        from custom_components.frank_energie_slim.sensor import async_setup_entry

        # Call async_setup_entry to initialize the integration
        async_add_entities = MagicMock()
        entry = MagicMock()
        entry.data = {"username": test_username, "password": test_password}

        # This should trigger the re-authentication logic
        await async_setup_entry(hass, entry, async_add_entities)

        # Verify that login was called with the correct credentials
        login_calls = [call for call in hass.async_add_executor_job.call_args_list 
                      if call[0][0] == client.login]
        self.assertTrue(any(call[0][1:] == (test_username, test_password) for call in login_calls))

        # Verify that after re-authentication, the operation was retried
        session_calls = [call for call in hass.async_add_executor_job.call_args_list 
                        if call[0][0] == client.get_smart_battery_sessions]
        self.assertGreaterEqual(len(session_calls), 1)

if __name__ == "__main__":
    unittest.main()
