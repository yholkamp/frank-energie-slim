from homeassistant import config_entries
import voluptuous as vol
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
import logging

_LOGGER = logging.getLogger(__name__)

class FrankEnergieConfigFlow(config_entries.ConfigFlow, domain="frank_energie_slim"):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            from .api import FrankEnergie
            api = FrankEnergie()
            try:
                auth = await self.hass.async_add_executor_job(
                    api.login, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
            except Exception as exc:
                # Log the full exception for debugging
                _LOGGER.error(f"Authentication/setup error: {exc}", exc_info=True)
                # Provide a detailed error message to the user
                errors["base"] = f"Loginfout: {str(exc)}"
            if not errors:
                return self.async_create_entry(title="Frank Energie Slim Handelen", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )