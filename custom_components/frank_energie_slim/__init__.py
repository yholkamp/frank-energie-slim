# Initialize the Frank Energie Slim package

async def _frank_energie_load_data(hass, client):
    """Fetch data and update entities for Frank Energie."""
    # No longer needed: entity setup is now handled in sensor.py
    pass

async def async_setup(hass, config):
    """Set up the Frank Energie integration."""
    conf = config.get("frank_energie")
    if conf is None:
        return True
    # No longer needed: entity setup is now handled in sensor.py
    return True

async def async_setup_entry(hass, entry):
    """Set up Frank Energie from a config entry."""
    # Delegate entity setup to sensor.py
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True