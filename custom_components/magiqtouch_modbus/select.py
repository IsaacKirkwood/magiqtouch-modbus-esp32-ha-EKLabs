import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MTMODCoordinator

DOMAIN = "magiqtouch_modbus"
HOME_ASSISTANT = "Home Assistant"
WALL_CONTROLLER = "Wall controller"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MagiqCoolControlSource(coordinator, config_entry)])


class MagiqCoolControlSource(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Control source"
    _attr_icon = "mdi:swap-horizontal-bold"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = [HOME_ASSISTANT, WALL_CONTROLLER]

    def __init__(self, coordinator: MTMODCoordinator, config_entry):
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_control_source"
        self.api_url = config_entry.data["HVAC URL"]

    @property
    def available(self):
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get("controller_protocol") == "magiqcool"
        )

    @property
    def current_option(self):
        if self.coordinator.data is None:
            return None
        if self.coordinator.data.get("magiqcool_override", False):
            return HOME_ASSISTANT
        return WALL_CONTROLLER

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.api_url)},
            name="Magiqtouch ESP32 Controller",
            model="Modbus ESP32 Interface",
            configuration_url=self.api_url,
        )

    async def async_select_option(self, option: str):
        payload = "override=on" if option == HOME_ASSISTANT else "override=off"
        command_url = self.api_url.rstrip("/") + "/command"
        session = aiohttp_client.async_get_clientsession(self.hass)

        try:
            async with session.post(
                command_url,
                data=payload,
                headers={"Content-Type": "text/plain"},
            ) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "Failed to select control source %s. Server returned %s",
                        option,
                        response.status,
                    )
                    return
        except Exception:
            _LOGGER.exception("Failed to select MagIQcool control source %s", option)
            return

        await self.coordinator.async_request_refresh()
