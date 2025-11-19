from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_SOURCE_ENTITY

class RealLastChangedFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Real Last Changed."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            entity_id = user_input[CONF_SOURCE_ENTITY]
            await self.async_set_unique_id(entity_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Real Last Changed: {entity_id}",
                data=user_input,
            )

        schema = vol.Schema({
            CONF_SOURCE_ENTITY: selector.selector({"entity": {}})
        })

        return self.async_show_form(step_id="user", data_schema=schema)
