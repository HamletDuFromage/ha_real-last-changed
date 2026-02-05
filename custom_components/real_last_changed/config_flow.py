from __future__ import annotations
import re
import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.helpers import selector, entity_registry as er, device_registry as dr
from homeassistant.util import slugify
from homeassistant.const import CONF_NAME
from .const import DOMAIN, CONF_SOURCE_ENTITY, CONF_SOURCE_ENTITIES, CONF_DEVICE_ID, CONF_FROM_STATE, CONF_TO_STATE


class RealLastChangedFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Real Last Changed."""

    VERSION = 1

    def __init__(self):
        self._matched = []

    async def async_step_user(self, _=None):
        return self.async_show_menu(step_id="user", menu_options=["single", "pattern"])

    async def async_step_single(self, user_input=None):
        if user_input is not None:
            advanced = user_input.get("advanced_options", {})
            return await self._create_or_update(
                user_input[CONF_SOURCE_ENTITY], 
                user_input.get(CONF_NAME),
                advanced.get(CONF_FROM_STATE),
                advanced.get(CONF_TO_STATE)
            )

        return self.async_show_form(
            step_id="single",
            data_schema=vol.Schema({
                vol.Required(CONF_SOURCE_ENTITY): selector.EntitySelector(),
                vol.Optional(CONF_NAME): str,
                vol.Optional("advanced_options"): data_entry_flow.section(
                    vol.Schema({
                        vol.Optional(CONF_FROM_STATE): str,
                        vol.Optional(CONF_TO_STATE): str,
                    }), 
                    {"collapsed": True}
                ),
            }),
        )

    async def async_step_pattern(self, user_input=None):
        errors = {}
        if user_input is not None:
            pattern = user_input.get("pattern", "").strip()
            if not (matched := self._match_entities(pattern, user_input.get("regex", False))):
                errors["base"] = "no_pattern" if not pattern else "no_matches"
            else:
                self._matched = matched
                advanced = user_input.get("advanced_options", {})
                self._filter_data = {
                    CONF_FROM_STATE: advanced.get(CONF_FROM_STATE),
                    CONF_TO_STATE: advanced.get(CONF_TO_STATE),
                }
                return await self.async_step_confirm()

        return self.async_show_form(
            step_id="pattern",
            data_schema=vol.Schema({
                vol.Required("pattern"): str,
                vol.Optional("regex", default=False): bool,
                vol.Optional("advanced_options"): data_entry_flow.section(
                    vol.Schema({
                        vol.Optional(CONF_FROM_STATE): str,
                        vol.Optional(CONF_TO_STATE): str,
                    }), 
                    {"collapsed": True}
                ),
            }),
            errors=errors,
        )

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            return await self._create_bulk(self._matched, self._filter_data)

        preview = "\n".join(f"• {e}" for e in self._matched[:30])
        if len(self._matched) > 30:
            preview += f"\n... and {len(self._matched) - 30} more"

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({}),
            description_placeholders={"count": str(len(self._matched)), "entities": preview},
        )

    def _match_entities(self, pattern: str, use_regex: bool) -> list[str]:
        matched = []
        for eid in self.hass.states.async_entity_ids():
            if self._is_rlc_entity(eid):
                continue
            try:
                if use_regex and re.search(pattern, eid, re.IGNORECASE):
                    matched.append(eid)
                elif not use_regex and pattern.lower() in eid.lower():
                    matched.append(eid)
            except re.error:
                pass
        return sorted(matched)

    def _is_rlc_entity(self, eid: str) -> bool:
        entry = er.async_get(self.hass).async_get(eid)
        return entry is not None and entry.platform == DOMAIN

    def _get_tracked_entities(self) -> set[str]:
        tracked = set()
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            tracked.update(entry.data.get(CONF_SOURCE_ENTITIES, []))
            if CONF_SOURCE_ENTITY in entry.data:
                tracked.add(entry.data[CONF_SOURCE_ENTITY])
        return tracked

    def _get_device_entry(self, device_id: str, from_state: str | None, to_state: str | None):
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.data.get(CONF_DEVICE_ID) != device_id:
                continue
            
            if self._entry_matches_states(entry, from_state, to_state):
                return entry
        return None

    def _entry_matches_states(self, entry, from_state: str | None, to_state: str | None) -> bool:
        e_from = entry.data.get(CONF_FROM_STATE) or None
        e_to = entry.data.get(CONF_TO_STATE) or None
        t_from = from_state or None
        t_to = to_state or None
        return e_from == t_from and e_to == t_to
        return None

    def _get_entities_from_entry(self, entry) -> list[str]:
        ents = list(entry.data.get(CONF_SOURCE_ENTITIES, []))
        if not ents and CONF_SOURCE_ENTITY in entry.data:
            ents = [entry.data[CONF_SOURCE_ENTITY]]
        return ents

    def _get_device_name(self, device_id: str) -> str:
        device = dr.async_get(self.hass).async_get(device_id)
        return device.name_by_user or device.name or device_id if device else device_id

    def _is_duplicated(self, entity_id: str, from_state: str | None, to_state: str | None) -> bool:
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            ignored_entities = entry.data.get(CONF_SOURCE_ENTITIES, [])
            if CONF_SOURCE_ENTITY in entry.data:
                ignored_entities.append(entry.data[CONF_SOURCE_ENTITY])
            
            if entity_id not in ignored_entities:
                continue

            # Check if states match
            if self._entry_matches_states(entry, from_state, to_state):
                return True
        return False

    async def _create_or_update(self, entity_id: str, name: str | None = None, from_state: str | None = None, to_state: str | None = None):
        if self._is_rlc_entity(entity_id):
            return self.async_abort(reason="cannot_track_self")
        
        # Global duplicate check
        if self._is_duplicated(entity_id, from_state, to_state):
             return self.async_abort(reason="already_configured")

        entry = er.async_get(self.hass).async_get(entity_id)
        device_id = entry.device_id if entry else None

        if device_id and (existing := self._get_device_entry(device_id, from_state, to_state)):
            await self._update_entry(existing, [entity_id])
            return self.async_abort(reason="added_to_device", description_placeholders={"count": "1"})

        if name:
            await self.async_set_unique_id(slugify(name))
            self._abort_if_unique_id_configured()

        data = {
            CONF_SOURCE_ENTITIES: [entity_id], 
            CONF_DEVICE_ID: device_id,
            CONF_FROM_STATE: from_state,
            CONF_TO_STATE: to_state,
        }
        if name:
            data[CONF_NAME] = name

        return self.async_create_entry(
            title=name or self._get_device_name(device_id) or entity_id,
            data=data,
        )

    async def _update_entry(self, entry, new_entities: list[str]):
        new_data = dict(entry.data)
        new_data[CONF_SOURCE_ENTITIES] = self._get_entities_from_entry(entry) + new_entities
        new_data.pop(CONF_SOURCE_ENTITY, None)
        self.hass.config_entries.async_update_entry(entry, data=new_data)
        await self.hass.config_entries.async_reload(entry.entry_id)

    async def _create_bulk(self, entities: list[str], filter_data: dict | None = None):
        ent_reg, by_device = er.async_get(self.hass), {}
        for eid in entities:
            entry = ent_reg.async_get(eid)
            by_device.setdefault(entry.device_id if entry else None, []).append(eid)

        created, added = 0, 0
        from_s = filter_data.get(CONF_FROM_STATE) if filter_data else None
        to_s = filter_data.get(CONF_TO_STATE) if filter_data else None

        for dev_id, eids in by_device.items():
            valid_eids = [e for e in eids if not self._is_duplicated(e, from_s, to_s)]
            if not valid_eids:
                continue

            if dev_id and (existing := self._get_device_entry(dev_id, from_s, to_s)):
                current_ents = self._get_entities_from_entry(existing)
                to_add = [e for e in valid_eids if e not in current_ents]
                if to_add:
                    await self._update_entry(existing, to_add)
                    added += len(to_add)
            else:
                data = {CONF_SOURCE_ENTITIES: valid_eids, CONF_DEVICE_ID: dev_id}
                if filter_data:
                    data.update(filter_data)
                self.hass.async_create_task(self.hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": "import"},
                    data=data,
                ))
                created += 1

        return self.async_abort(reason="bulk_created", description_placeholders={"created": str(created), "added": str(added)})

    async def async_step_import(self, data: dict):
        ents, dev_id = data.get(CONF_SOURCE_ENTITIES, []), data.get(CONF_DEVICE_ID)
        
        base_id = f"device_{dev_id}" if dev_id else ents[0]
        from_s = data.get(CONF_FROM_STATE)
        to_s = data.get(CONF_TO_STATE)
        suffix = ""
        if from_s or to_s:
            suffix = f"_{slugify(from_s or 'any')}_{slugify(to_s or 'any')}"
            
        await self.async_set_unique_id(f"{base_id}{suffix}")
        self._abort_if_unique_id_configured()
        title = self._get_device_name(dev_id) if dev_id else ents[0]
        return self.async_create_entry(title=title, data=data)
