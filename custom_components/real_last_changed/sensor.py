from __future__ import annotations
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback, State
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util
from homeassistant.const import STATE_UNKNOWN, STATE_UNAVAILABLE
from .const import CONF_SOURCE_ENTITY

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up sensor for a config entry."""
    source = entry.data[CONF_SOURCE_ENTITY]
    sensor = RealLastChangedSensor(source)
    async_add_entities([sensor])

class RealLastChangedSensor(RestoreEntity, SensorEntity):
    """Sensor that tracks true last_changed for any entity."""

    _attr_should_poll = False
    _attr_native_unit_of_measurement = None
    _attr_device_class = "timestamp"

    def __init__(self, source_entity: str):
        self._source = source_entity
        self._attr_name = f"{source_entity.split('.')[-1]}_real_last_changed"
        self._attr_unique_id = f"{source_entity.replace('.', '_')}_real_last_changed"
        self._attr_native_value = None
        self._previous_valid_state = None
        self._unsubscribe = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {"previous_valid_state": self._previous_valid_state}

    async def async_added_to_hass(self):
        """Restore previous state and track changes."""
        await super().async_added_to_hass()

        # Restore previous timestamp and valid state if exists
        if (state := await self.async_get_last_state()) is not None:
            self._attr_native_value = dt_util.parse_datetime(state.state)
            self._previous_valid_state = state.attributes.get("previous_valid_state")

        # Track state changes
        @callback
        def _state_changed(event):

            new: State | None = event.data.get("new_state")
            
            if new is None or new.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                return

            if self._previous_valid_state != new.state:
                self._previous_valid_state = new.state
                self._attr_native_value = datetime.now().astimezone()
                self.async_write_ha_state()

        self._unsubscribe = async_track_state_change_event(
            self.hass, [self._source], _state_changed
        )

    async def async_will_remove_from_hass(self):
        """Cleanup subscriptions."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
