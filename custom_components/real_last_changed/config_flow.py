from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector, entity_registry as er, device_registry as dr
from homeassistant.const import CONF_NAME
from homeassistant.util import slugify
from .const import DOMAIN, CONF_SOURCE_ENTITY, CONF_DEVICE_ID

class RealLastChangedFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Real Last Changed."""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self._user_input = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._user_input = user_input
            entity_id = user_input[CONF_SOURCE_ENTITY]
            
            # Check if entity belongs to a device
            ent_reg = er.async_get(self.hass)
            entry = ent_reg.async_get(entity_id)
            
            if entry and entry.device_id:
                return await self.async_step_device_link()
            
            return self._async_create_entry()

        schema = vol.Schema({
            vol.Required(CONF_SOURCE_ENTITY): selector.selector({"entity": {}}),
            vol.Optional(CONF_NAME): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_device_link(self, user_input=None):
        """Handle device link step."""
        entity_id = self._user_input[CONF_SOURCE_ENTITY]
        ent_reg = er.async_get(self.hass)
        entry = ent_reg.async_get(entity_id)
        device_id = entry.device_id
        
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get(device_id)
        device_name = device.name_by_user or device.name or "Unknown Device"

        if user_input is not None:
            if user_input["link_device"]:
                self._user_input[CONF_DEVICE_ID] = device_id
            
            return self._async_create_entry()

        return self.async_show_form(
            step_id="device_link",
            data_schema=vol.Schema({
                vol.Required("link_device", default=True): bool,
            }),
            description_placeholders={
                "device_name": device_name,
            },
        )

    def _async_create_entry(self):
        """Create the config entry."""
        entity_id = self._user_input[CONF_SOURCE_ENTITY]
        name = self._user_input.get(CONF_NAME)
        if name:
            unique_id = slugify(name)
        else:
            unique_id = entity_id
        
        self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        
        return self.async_create_entry(
            title=f"Real Last Changed: {entity_id}",
            data=self._user_input,
        )
