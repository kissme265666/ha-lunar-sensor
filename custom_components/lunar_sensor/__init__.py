"""农历传感器自定义集成"""
import asyncio
from pathlib import Path
import shutil

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import STORAGE_DIR

DOMAIN = "lunar_sensor"


def _sync_brand_icons(hass: HomeAssistant) -> None:
    """Copy bundled icon files into the Home Assistant brands cache.

    Home Assistant loads integration icons from the brands API cache
    (``.storage/brand_cache/<domain>/``). Custom integrations that are not
    published in the official brands repository need to populate this
    cache themselves, otherwise the integration card shows an empty icon.
    """
    component_dir = Path(__file__).parent.resolve()
    brand_dir = Path(hass.config.path(STORAGE_DIR)) / "brand_cache" / DOMAIN
    brand_dir.mkdir(parents=True, exist_ok=True)

    for filename in ("icon.png", "icon@2x.png", "logo.png"):
        source = component_dir / filename
        dest = brand_dir / filename
        if source.exists():
            try:
                shutil.copy2(source, dest)
            except OSError:
                pass


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lunar_sensor from a config entry."""
    await hass.async_add_executor_job(_sync_brand_icons, hass)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
