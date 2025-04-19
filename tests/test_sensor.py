import unittest
from unittest.mock import patch
from custom_components.frank_energie_slim.sensor import FrankEnergieBatterySessionResultSensor
from custom_components.frank_energie_slim.entities import (
    FrankEnergieBatterySessionSensor,
    FrankEnergieBatterySessionResultSensor,
    FrankEnergieBatteryModeSensor,
    FrankEnergieBatteryStateOfChargeSensor,
    FrankEnergieTotalResultSensor,
    FrankEnergieTotalAvgSocSensor,
    FrankEnergieTotalLastModeSensor,
)

class TestFrankEnergieBatterySessionResultSensor(unittest.TestCase):
    @patch('custom_components.frank_energie_slim.api.requests.post')
    def test_battery_session_result_sensors(self, mock_post):
        # Load mock session data as would be returned by the API
        session = {
            "deviceId": "id123",
            "periodStartDate": "2025-04-18",
            "periodEndDate": "2025-04-18",
            "periodEpexResult": -0.10908,
            "periodFrankSlim": 0.05807999999999999,
            "periodImbalanceResult": 0.24638372,
            "periodTotalResult": 0.19538371999999998,
        }
        # Test each result sensor
        sensors = [
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodEpexResult', 'epex'), -0.10908, 'EPEX-correctie vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodFrankSlim', 'frankslim'), 0.05807999999999999, 'Frank Slim vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodImbalanceResult', 'handelsresultaat'), 0.24638372, 'Handelsresultaat vandaag'),
            (FrankEnergieBatterySessionResultSensor(None, session, 'periodTotalResult', 'nettoresultaat'), 0.19538371999999998, 'Totaalresultaat vandaag'),
        ]
        for sensor, expected_state, expected_name in sensors:
            self.assertEqual(sensor.state, expected_state)
            self.assertEqual(sensor._attr_name, expected_name)

class TestFrankEnergieEntities(unittest.TestCase):
    def setUp(self):
        self.session = {
            "deviceId": "id123",
            "periodStartDate": "2025-04-18",
            "periodEndDate": "2025-04-18",
            "periodEpexResult": -0.10908,
            "periodFrankSlim": 0.05808,
            "periodImbalanceResult": 0.24638,
            "periodTotalResult": 0.19538,
            "periodTradingResult": 0.30446,
            "totalTradingResult": 22.31,
        }
        self.details = {
            "smartBattery": {"brand": "SolarEdge", "provider": "SOLAREDGE", "settings": {"batteryMode": "auto"}},
            "smartBatterySummary": {"lastKnownStateOfCharge": 77}
        }

    def test_battery_session_sensor(self):
        sensor = FrankEnergieBatterySessionSensor(None, self.session, self.details)
        self.assertEqual(sensor.state, 22.31)
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "Handelsresultaat totaal")

    def test_battery_mode_sensor(self):
        sensor = FrankEnergieBatteryModeSensor(None, "id123", "auto", self.details)
        self.assertEqual(sensor.state, "auto")
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "Thuisbatterij modus")

    def test_battery_soc_sensor(self):
        sensor = FrankEnergieBatteryStateOfChargeSensor(None, "id123", 77, self.details)
        self.assertEqual(sensor.state, 77)
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "Thuisbatterij SoC")
        self.assertEqual(sensor._attr_unit_of_measurement, "%")

    def test_battery_session_result_sensor(self):
        sensor = FrankEnergieBatterySessionResultSensor(None, self.session, 'periodEpexResult', 'epex', self.details)
        self.assertEqual(sensor.state, -0.10908)
        self.assertIn("SolarEdge", sensor.device_info["name"])
        self.assertEqual(sensor._attr_name, "EPEX-correctie vandaag")
        self.assertEqual(sensor._attr_unit_of_measurement, "EUR")

    def test_total_result_sensor(self):
        sensor = FrankEnergieTotalResultSensor(None, 'periodEpexResult')
        self.assertEqual(sensor._attr_name, "EPEX-correctie vandaag")
        self.assertEqual(sensor._attr_unit_of_measurement, "EUR")
        self.assertEqual(sensor.device_info["name"], "Totaal batterijen")
        self.assertIsNone(sensor.state)

    def test_total_avg_soc_sensor(self):
        sensor = FrankEnergieTotalAvgSocSensor(None)
        sensor._state = 55.5
        self.assertEqual(sensor.state, 55.5)
        self.assertEqual(sensor._attr_name, "Gemiddelde SoC batterijen")
        self.assertEqual(sensor.device_info["name"], "Totaal batterijen")
        self.assertEqual(sensor._attr_unit_of_measurement, "%")

    def test_total_last_mode_sensor(self):
        sensor = FrankEnergieTotalLastModeSensor(None)
        sensor._state = "auto"
        self.assertEqual(sensor.state, "auto")
        self.assertEqual(sensor._attr_name, "Laatste batterijmodus")
        self.assertEqual(sensor.device_info["name"], "Totaal batterijen")

if __name__ == "__main__":
    unittest.main()
