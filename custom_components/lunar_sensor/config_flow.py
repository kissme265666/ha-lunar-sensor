"""Config flow for lunar_sensor integration."""
from homeassistant import config_entries
import voluptuous as vol

DOMAIN = "lunar_sensor"


class LunarSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for lunar_sensor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="农历传感器", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))
