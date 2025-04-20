from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from .api import FrankEnergie
from .entities import (
    FrankEnergieBatterySessionSensor,
    FrankEnergieBatterySessionResultSensor,
    FrankEnergieTotalResultSensor,
    FrankEnergieBatteryModeSensor,
    FrankEnergieBatteryStateOfChargeSensor,
    FrankEnergieTotalAvgSocSensor,
    FrankEnergieTotalLastModeSensor,
    FrankEnergieTotalLastUpdateSensor,
)
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Map from API response field to entity name suffix
RESULT_SENSOR_MAP = {
    'periodEpexResult': 'epex',
    'periodFrankSlim': 'frankslim',
    'periodImbalanceResult': 'handelsresultaat',
    'periodTradingResult': 'brutoresultaat',
    'periodTotalResult': 'nettoresultaat',
}
SESSION_RESULT_KEYS = list(RESULT_SENSOR_MAP.keys())

@dataclass
class BatteryEntityGroup:
    mode_sensor: object
    soc_sensor: object
    session_sensor: object
    result_sensors: list

def get_battery_mode_from_settings(settings):
    """Return a normalized mode string based on battery settings."""
    battery_mode = (settings.get('batteryMode') or '').upper()
    strategy = (settings.get('imbalanceTradingStrategy') or '').upper()
    self_consumption = settings.get('selfConsumptionTradingAllowed')
    if battery_mode == 'IMBALANCE_TRADING':
        if strategy == 'AGGRESSIVE':
            return 'imbalance_aggressive'
        else:
            return 'imbalance'
    elif self_consumption:
        return 'self_consumption_plus'
    return battery_mode.lower() if battery_mode else None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Frank Energie integration and sensors."""
    _LOGGER.info("Setting up Frank Energie entry")
    username = entry.data.get("username")
    password = entry.data.get("password")
    client = FrankEnergie()
    await hass.async_add_executor_job(client.login, username, password)
    data = await hass.async_add_executor_job(client.get_smart_batteries)
    batteries = data['data']['smartBatteries']
    entities = []
    battery_ids = []
    battery_details = []
    battery_entity_groups = []
    for battery in batteries:
        battery_ids.append(battery['id'])
        # Fetch battery details
        details_data = await hass.async_add_executor_job(client.get_smart_battery_details, battery['id'])
        details = details_data['data']
        battery_details.append(details)
        today = datetime.now()
        session_data = await hass.async_add_executor_job(
            client.get_smart_battery_sessions, battery['id'], today, today
        )
        session = session_data['data']['smartBatterySessions']
        # Extract mode and stateOfCharge
        smart_battery = details.get('smartBattery', {})
        summary = details.get('smartBatterySummary', {})
        settings = smart_battery.get('settings', {})
        # Determine mode using helper function
        mode = get_battery_mode_from_settings(settings)
        state_of_charge = summary.get('lastKnownStateOfCharge')
        # Create sensors
        mode_sensor = FrankEnergieBatteryModeSensor(hass, battery['id'], mode, details)
        soc_sensor = FrankEnergieBatteryStateOfChargeSensor(hass, battery['id'], state_of_charge, details)
        session_sensor = FrankEnergieBatterySessionSensor(hass, session, details)
        result_sensors = [
            FrankEnergieBatterySessionResultSensor(hass, session, result_key, suffix, details)
            for result_key, suffix in RESULT_SENSOR_MAP.items()
        ]
        group = BatteryEntityGroup(mode_sensor, soc_sensor, session_sensor, result_sensors)
        battery_entity_groups.append(group)
        entities.extend([mode_sensor, soc_sensor, session_sensor] + result_sensors)

        # Add total result sensors using the map
        total_entities = [
            FrankEnergieTotalResultSensor(hass, result_key, suffix)
            for result_key, suffix in RESULT_SENSOR_MAP.items()
        ]
        entities.extend(total_entities)

    # Add total avg soc, last mode, and last update sensors
    total_avg_soc_entity = FrankEnergieTotalAvgSocSensor(hass)
    total_last_mode_entity = FrankEnergieTotalLastModeSensor(hass)
    total_last_update_entity = FrankEnergieTotalLastUpdateSensor(hass)
    entities.extend([total_avg_soc_entity, total_last_mode_entity, total_last_update_entity])

    async_add_entities(entities, update_before_add=True)

    # Store for periodic update
    hass.data.setdefault("frank_energie_slim", {})[entry.entry_id] = {
        "client": client,
        "battery_ids": battery_ids,
        "entities": entities,
        "total_entities": total_entities,
        "battery_details": battery_details,
    }

    def calc_avg_soc_and_last_mode(socs, modes):
        """Calculate average state of charge and last mode from lists."""
        avg_soc = sum([s for s in socs if s is not None]) / len([s for s in socs if s is not None]) if socs else None
        last_mode = modes[-1] if modes else None
        return avg_soc, last_mode

    async def fetch_battery_data(fetch_details=True):
        """Fetch session, mode, and state of charge for all batteries."""
        sessions, modes, socs = [], [], []
        for i, battery_id in enumerate(battery_ids):
            today = datetime.now()
            session_data = await hass.async_add_executor_job(
                client.get_smart_battery_sessions, battery_id, today, today
            )
            if fetch_details:
                details_data = await hass.async_add_executor_job(client.get_smart_battery_details, battery_id)
                details = details_data['data']
            else:
                details = battery_details[i]
            smart_battery = details.get('smartBattery', {})
            summary = details.get('smartBatterySummary', {})
            settings = smart_battery.get('settings', {})
            # Determine mode using helper function
            mode = get_battery_mode_from_settings(settings)
            state_of_charge = summary.get('lastKnownStateOfCharge')
            modes.append(mode)
            socs.append(state_of_charge)
            session = session_data['data']['smartBatterySessions']
            sessions.append(session)
        return sessions, modes, socs

    def update_battery_entities(battery_entity_groups, sessions, modes, socs):
        """Update all battery-related sensor entities with new data."""
        for i, group in enumerate(battery_entity_groups):
            session = sessions[i]
            mode = modes[i]
            state_of_charge = socs[i]
            group.mode_sensor._state = mode
            group.soc_sensor._state = state_of_charge
            group.session_sensor._session = session
            group.session_sensor._state = session['totalTradingResult']
            for idx, key in enumerate(SESSION_RESULT_KEYS):
                group.result_sensors[idx]._session = session
                group.result_sensors[idx]._state = session[key]
                group.result_sensors[idx]._attr_extra_state_attributes = {}
            for entity in [group.mode_sensor, group.soc_sensor, group.session_sensor] + group.result_sensors:
                entity.async_write_ha_state()

    def update_total_entities(total_entities, sessions, modes, socs):
        """Update all total result sensor entities with aggregated data, and update avg soc/mode sensors."""
        avg_soc, last_mode = calc_avg_soc_and_last_mode(socs, modes)
        for idx, key in enumerate(SESSION_RESULT_KEYS):
            total = sum(float(session.get(key, 0) or 0) for session in sessions)
            total_entities[idx]._state = total
            total_entities[idx].async_write_ha_state()
        total_avg_soc_entity._state = avg_soc
        total_avg_soc_entity.async_write_ha_state()
        total_last_mode_entity._state = last_mode
        total_last_mode_entity.async_write_ha_state()
        # Set the most recent lastUpdate from all battery_details
        last_updates = [
            details.get('smartBatterySummary', {}).get('lastUpdate')
            for details in battery_details
            if details.get('smartBatterySummary', {}).get('lastUpdate')
        ]
        if last_updates:
            # ISO8601 strings, so max() gives the latest
            total_last_update_entity._state = max(last_updates)
        else:
            total_last_update_entity._state = None
        total_last_update_entity.async_write_ha_state()

    async def update_totals():
        """Update total sensors immediately after setup using cached battery details."""
        sessions, modes, socs = await fetch_battery_data(fetch_details=False)
        update_total_entities(total_entities, sessions, modes, socs)

    # Immediately update totals after setup
    hass.async_create_task(update_totals())

    async def _refresh_sensors(now):
        """Periodic update of all battery and total sensors."""
        sessions, modes, socs = await fetch_battery_data(fetch_details=True)
        _LOGGER.info(f"All sessions collected for totals: {sessions}")
        update_battery_entities(battery_entity_groups, sessions, modes, socs)
        update_total_entities(total_entities, sessions, modes, socs)

    async_track_time_interval(hass, _refresh_sensors, timedelta(minutes=5))