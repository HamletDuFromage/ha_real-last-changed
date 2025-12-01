from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.const import CONF_NAME
from homeassistant.util import slugify
from .const import DOMAIN, CONF_SOURCE_ENTITY

class RealLastChangedFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Real Last Changed."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            entity_id = user_input[CONF_SOURCE_ENTITY]
            name = user_input.get(CONF_NAME)
            if name:
                unique_id = slugify(name)
            else:
                unique_id = entity_id
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Real Last Changed: {entity_id}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_SOURCE_ENTITY): selector.selector({"entity": {}}),
            vol.Optional(CONF_NAME): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
