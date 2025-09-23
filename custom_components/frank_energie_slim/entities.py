from homeassistant.helpers.entity import Entity, generate_entity_id
import voluptuous as vol
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

ENTITY_NAMES = {
    'periodEpexResult': 'EPEX-correctie vandaag',
    'periodFrankSlim': 'Frank Slim vandaag',
    'periodImbalanceResult': 'Handelsresultaat vandaag',
    'periodTotalResult': 'Totaalresultaat vandaag',
    'periodTradingResult': 'Brutoresultaat vandaag',
}

class FrankEnergieBatterySessionResultSensor(Entity):
    def __init__(self, hass, session, result_key, unique_id_suffix, details=None):
        self.hass = hass
        self._session = session
        self._result_key = result_key
        self._details = details or {}
        device_id = session.get('deviceId')
        self._attr_name = ENTITY_NAMES.get(result_key, result_key)
        self._attr_unique_id = f"battery_{device_id}_{unique_id_suffix}"
        self._attr_has_entity_name = True
        self._state = session.get(result_key)
        self._attr_device_class = "monetary"
        self._attr_unit_of_measurement = "EUR"
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', f"{device_id}_{unique_id_suffix}", hass=hass
            )
        else:
            self.entity_id = f"sensor.frank_slim_{device_id}_{unique_id_suffix}"

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        brand = self._details.get('smartBattery', {}).get('brand', 'Battery')
        device_id = str(self._session['deviceId'])
        return {
            "identifiers": {("frank_energie_slim", device_id)},
            "name": f"{brand} ({device_id})",
            "manufacturer": self._details.get('smartBattery', {}).get('provider', 'Frank Energie'),
            "model": brand,
        }

    async def async_update(self):
        pass

class FrankEnergieTotalAvgSocSensor(Entity):
    """Sensor for average state of charge across all batteries (totals device)."""
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "Gemiddelde SoC"
        self._attr_unique_id = "frank_energie_average_soc"
        self._attr_has_entity_name = True
        self._attr_unit_of_measurement = "%"
        self._state = None
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', 'average_soc', hass=hass
            )
        else:
            self.entity_id = 'sensor.frank_slim_average_soc'

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        return FrankEnergieTotalResultSensor.TOTALS_DEVICE_INFO

    async def async_update(self):
        pass

class FrankEnergieTotalLastModeSensor(Entity):
    """Sensor for last battery mode across all batteries (totals device)."""
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "Batterijmodus"
        self._attr_unique_id = "frank_energie_total_last_mode"
        self._attr_has_entity_name = True
        self._state = None
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', 'total_last_mode', hass=hass
            )
        else:
            self.entity_id = 'sensor.frank_slim_total_last_mode'

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        return FrankEnergieTotalResultSensor.TOTALS_DEVICE_INFO

    async def async_update(self):
        pass

class FrankEnergieTotalLastUpdateSensor(Entity):
    """Sensor for the most recent lastUpdate timestamp across all batteries (totals device)."""
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "Laatste update"
        self._attr_unique_id = "frank_energie_total_last_update"
        self._attr_has_entity_name = True
        self._attr_device_class = "timestamp"
        self._state = None
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', 'total_last_update', hass=hass
            )
        else:
            self.entity_id = 'sensor.frank_slim_total_last_update'

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        return FrankEnergieTotalResultSensor.TOTALS_DEVICE_INFO

    async def async_update(self):
        pass

class FrankEnergieTotalResultSensor(Entity):
    TOTALS_DEVICE_INFO = {
        "identifiers": {("frank_energie_slim", "totals")},
        "name": "Totaal batterijen",
        "manufacturer": "Frank Energie"
    }
    def __init__(self, hass, result_key, unique_id_suffix=None):
        self.hass = hass
        self._result_key = result_key
        self._attr_name = f"{ENTITY_NAMES.get(result_key, result_key)}"
        # Use unique_id_suffix for unique_id and entity_id if provided, else fallback to result_key
        suffix = unique_id_suffix if unique_id_suffix is not None else result_key
        self._attr_unique_id = f"frank_energie_{suffix}_total"
        self._attr_has_entity_name = True
        self._state = None  # Start as None, not 0.0
        self._attr_device_class = "monetary"
        self._attr_unit_of_measurement = "EUR"
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', f"{suffix}_total", hass=hass
            )
        else:
            self.entity_id = f"sensor.frank_slim_{suffix}_total"

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        return self.TOTALS_DEVICE_INFO

    async def async_update(self):
        pass

class FrankEnergieBatteryModeSensor(Entity):
    def __init__(self, hass, device_id, mode, details=None):
        self.hass = hass
        self._device_id = device_id
        self._details = details or {}
        self._state = mode
        self._attr_name = f"Batterijmodus"
        self._attr_unique_id = f"frank_energie_battery_{device_id}_mode"
        self._attr_has_entity_name = True
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', f"{device_id}_mode", hass=hass
            )
        else:
            self.entity_id = f"sensor.frank_slim_{device_id}_mode"

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        brand = self._details.get('smartBattery', {}).get('brand', 'Battery')
        return {
            "identifiers": {("frank_energie_slim", str(self._device_id))},
            "name": f"{brand} ({self._device_id})",
            "manufacturer": self._details.get('smartBattery', {}).get('provider', 'Frank Energie'),
            "model": brand,
        }

    async def async_update(self):
        pass

class FrankEnergieBatteryStateOfChargeSensor(Entity):
    def __init__(self, hass, device_id, state_of_charge, details=None):
        self.hass = hass
        self._device_id = device_id
        self._details = details or {}
        self._state = state_of_charge
        self._attr_name = f"State of Charge"
        self._attr_unique_id = f"frank_energie_battery_{device_id}_soc"
        self._attr_has_entity_name = True
        self._attr_unit_of_measurement = "%"
        if hass is not None:
            self.entity_id = generate_entity_id(
                'sensor.frank_slim_{}', f"{device_id}_soc", hass=hass
            )
        else:
            self.entity_id = f"sensor.frank_slim_{device_id}_soc"

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        brand = self._details.get('smartBattery', {}).get('brand', 'Battery')
        return {
            "identifiers": {("frank_energie_slim", str(self._device_id))},
            "name": f"{brand} ({self._device_id})",
            "manufacturer": self._details.get('smartBattery', {}).get('provider', 'Frank Energie'),
            "model": brand,
        }

    async def async_update(self):
        pass

class FrankEnergieConfigFlow:
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            from .api import FrankEnergie
            api = FrankEnergie()
            try:
                await self.hass.async_add_executor_job(
                    api.login, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
            except Exception:
                errors["base"] = "auth"
            if not errors:
                return self.async_create_entry(title="Frank Energie", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
