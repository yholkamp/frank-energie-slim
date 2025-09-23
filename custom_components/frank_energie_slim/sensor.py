from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from .api import FrankEnergie
from .entities import (
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
    'totalTradingResult': 'trading_result',
}
SESSION_RESULT_KEYS = list(RESULT_SENSOR_MAP.keys())

@dataclass
class BatteryEntityGroup:
    mode_sensor: object
    soc_sensor: object
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
    # Log battery discovery summary and handle no-battery case
    if not batteries:
        _LOGGER.error("No smart batteries were found. No battery sensors will be created. Please verify your Frank Energie account and configuration.")
    else:
        _LOGGER.info("Discovered %d smart battery(ies)", len(batteries))
    entities = []
    battery_ids = []
    battery_details = []
    battery_entity_groups = []

    # Create total result sensors only once (not per battery)
    total_entities = [
        FrankEnergieTotalResultSensor(hass, result_key, suffix)
        for result_key, suffix in RESULT_SENSOR_MAP.items()
    ]

    for battery in batteries:
        _LOGGER.info("Discovered battery with id: %s", battery.get('id'))
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
        result_sensors = [
            FrankEnergieBatterySessionResultSensor(hass, session, result_key, suffix, details)
            for result_key, suffix in RESULT_SENSOR_MAP.items()
        ]
        group = BatteryEntityGroup(mode_sensor, soc_sensor, result_sensors)
        battery_entity_groups.append(group)
        entities.extend([mode_sensor, soc_sensor] + result_sensors)

    # Add total result sensors only once
    entities.extend(total_entities)

    # Add total avg soc, last mode, and last update sensors
    total_avg_soc_entity = FrankEnergieTotalAvgSocSensor(hass)
    total_last_mode_entity = FrankEnergieTotalLastModeSensor(hass)
    total_last_update_entity = FrankEnergieTotalLastUpdateSensor(hass)
    entities.extend([total_avg_soc_entity, total_last_mode_entity, total_last_update_entity])

    for entity in entities:
        unique_id = getattr(entity, '_attr_unique_id', None)
        _LOGGER.info(f"Registered entity with unique_id: {unique_id} and entity_id: {getattr(entity, 'entity_id', None)}")

    async_add_entities(entities, update_before_add=True)

    # Store for periodic update
    hass.data.setdefault("frank_energie_slim", {})[entry.entry_id] = {
        "client": client,
        "battery_ids": battery_ids,
        "entities": entities,
        "total_entities": total_entities,
        "battery_details": battery_details,
        "username": username,
        "password": password,
    }

    def calc_avg_soc_and_last_mode(socs, modes):
        """Calculate average state of charge and last mode from lists."""
        avg_soc = sum([s for s in socs if s is not None]) / len([s for s in socs if s is not None]) if socs else None
        last_mode = modes[-1] if modes else None
        return avg_soc, last_mode

    async def fetch_battery_data(fetch_details=True):
        """Fetch session, mode, and state of charge for all batteries."""
        sessions, modes, socs = [], [], []
        new_battery_details = []  # Collect fresh details if fetch_details is True
        for i, battery_id in enumerate(battery_ids):
            today = datetime.now()
            try:
                session_data = await hass.async_add_executor_job(
                    client.get_smart_battery_sessions, battery_id, today, today
                )
                if fetch_details:
                    details_data = await hass.async_add_executor_job(client.get_smart_battery_details, battery_id)
                    details = details_data['data']
                    new_battery_details.append(details)
                else:
                    details = battery_details[i]
            except Exception as e:
                if str(e) == "Authentication required":
                    _LOGGER.info("Authentication token expired, attempting to re-authenticate")
                    # Get credentials from stored data
                    for entry_id, data in hass.data["frank_energie_slim"].items():
                        if data.get("client") == client:
                            username = data.get("username")
                            password = data.get("password")
                            break
                    else:
                        _LOGGER.error("Could not find credentials for re-authentication")
                        raise

                    # Re-authenticate
                    await hass.async_add_executor_job(client.login, username, password)

                    # Retry the operation
                    session_data = await hass.async_add_executor_job(
                        client.get_smart_battery_sessions, battery_id, today, today
                    )
                    if fetch_details:
                        details_data = await hass.async_add_executor_job(client.get_smart_battery_details, battery_id)
                        details = details_data['data']
                        new_battery_details.append(details)
                    else:
                        details = battery_details[i]
                else:
                    # Re-raise if it's not an authentication error
                    raise
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
        # If we fetched new details, update battery_details in-place
        if fetch_details and new_battery_details:
            battery_details.clear()
            battery_details.extend(new_battery_details)
        return sessions, modes, socs

    def update_battery_entities(battery_entity_groups, sessions, modes, socs):
        """Update all battery-related sensor entities with new data."""
        for i, group in enumerate(battery_entity_groups):
            session = sessions[i]
            mode = modes[i]
            state_of_charge = socs[i]
            group.mode_sensor._state = mode
            group.soc_sensor._state = state_of_charge
            for idx, key in enumerate(SESSION_RESULT_KEYS):
                group.result_sensors[idx]._session = session
                group.result_sensors[idx]._state = session[key]
                group.result_sensors[idx]._attr_extra_state_attributes = {}
            for entity in [group.mode_sensor, group.soc_sensor] + group.result_sensors:
                if getattr(entity, 'hass', None) is not None:
                    entity.async_write_ha_state()

    def update_total_entities(total_entities, sessions, modes, socs):
        """Update all total result sensor entities with aggregated data, and update avg soc/mode sensors."""
        avg_soc, last_mode = calc_avg_soc_and_last_mode(socs, modes)
        for idx, key in enumerate(SESSION_RESULT_KEYS):
            total = sum(float(session.get(key, 0) or 0) for session in sessions)
            total_entities[idx]._state = total
            if getattr(total_entities[idx], 'hass', None) is not None:
                total_entities[idx].async_write_ha_state()
        total_avg_soc_entity._state = avg_soc
        if getattr(total_avg_soc_entity, 'hass', None) is not None:
            total_avg_soc_entity.async_write_ha_state()
        total_last_mode_entity._state = last_mode
        if getattr(total_last_mode_entity, 'hass', None) is not None:
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
        if getattr(total_last_update_entity, 'hass', None) is not None:
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
