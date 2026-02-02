from __future__ import annotations
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from .const import CONF_SOURCE_ENTITY, CONF_SOURCE_ENTITIES, CONF_DEVICE_ID


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up sensors for a config entry."""
    device_id = entry.data.get(CONF_DEVICE_ID)

    device_info = None
    if device_id:
        dev_reg = dr.async_get(hass)
        if device := dev_reg.async_get(device_id):
            if device.identifiers:
                device_info = dr.DeviceInfo(identifiers=device.identifiers)

    # Support both V1 (single) and V2 (list) formats
    entities = []
    if CONF_SOURCE_ENTITIES in entry.data:
        entities = entry.data[CONF_SOURCE_ENTITIES]
    elif CONF_SOURCE_ENTITY in entry.data:
        entities = [entry.data[CONF_SOURCE_ENTITY]]

    sensors = [RealLastChangedSensor(e, device_info) for e in entities]
    async_add_entities(sensors)


class RealLastChangedSensor(RestoreEntity, SensorEntity):
    """Sensor that tracks true last_changed for any entity."""

    _attr_should_poll = False
    _attr_device_class = "timestamp"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, source_entity: str, device_info: dr.DeviceInfo | None = None):
        self._source = source_entity
        self._attr_device_info = device_info
        self._attr_name = f"{source_entity.split('.')[-1]}_real_last_changed"
        self._attr_unique_id = f"{source_entity.replace('.', '_')}_real_last_changed"
        self._attr_native_value = None
        self._previous_state = None
        self._unsub = None

    @property
    def extra_state_attributes(self):
        return {"previous_valid_state": self._previous_state}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        if (state := await self.async_get_last_state()) is not None:
            self._attr_native_value = dt_util.parse_datetime(state.state)
            self._previous_state = state.attributes.get("previous_valid_state")

        @callback
        def on_state_change(event):
            new = event.data.get("new_state")
            if new is None or new.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                return
            if self._previous_state != new.state:
                self._previous_state = new.state
                self._attr_native_value = datetime.now().astimezone()
                self.async_write_ha_state()

        self._unsub = async_track_state_change_event(self.hass, [self._source], on_state_change)

    async def async_will_remove_from_hass(self):
        if self._unsub:
            self._unsub()
