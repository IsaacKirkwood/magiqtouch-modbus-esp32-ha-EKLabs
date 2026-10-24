import asyncio
import logging

from datetime import timedelta

from aiohttp import ClientError, ClientTimeout

from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

DOMAIN = "magiqtouch_modbus"
_LOGGER = logging.getLogger(__name__)

class MTMODCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry):
        super().__init__(
            hass,
            logger=_LOGGER,  # your logger
            name="MTMOD Coordinator",
            update_method=self._async_update,
            update_interval=timedelta(seconds=5),
        )
        self.entry = config_entry
        self.url = config_entry.data["HVAC URL"]
        self.session = aiohttp_client.async_get_clientsession(hass)
        self.lastresult = None
        self.failcount = 0
        # Blocks climate commands immediately while a Wall controller selection
        # is in flight, before the next status poll sees override=off.
        self.wall_control_requested = False

    async def _async_update(self):
        timeout = ClientTimeout(total=20, connect=5, sock_read=15)
        try:
            async with self.session.get(self.url, timeout=timeout) as response:
                response.raise_for_status()
                self.lastresult = await response.json(content_type=None)
                self.failcount = 0
            if (
                self.lastresult.get("ha_heartbeat_supported")
                and self.lastresult.get("magiqcool_override")
                and not self.wall_control_requested
            ):
                async with self.session.post(
                    self.url.rstrip("/") + "/command",
                    data="heartbeat=ha",
                    headers={"Content-Type": "text/plain"},
                    timeout=timeout,
                ) as heartbeat_response:
                    heartbeat_response.raise_for_status()
                    await heartbeat_response.read()
            return self.lastresult
        except (ClientError, asyncio.TimeoutError) as ex:
            _LOGGER.warning("Error getting status from HVAC Magiqtouch Modbus Interface: %s", ex)
            if self.failcount < 5:
                self.failcount += 1
                return self.lastresult
            return None
