"""农历传感器自定义集成"""
from pathlib import Path
import shutil

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import STORAGE_DIR

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lunar_sensor"


def _sync_brand_icons(hass: HomeAssistant) -> None:
    """Copy bundled icon files into the Home Assistant brands cache.

    HA caches brand icons in ``.cache/brands/integrations/<domain>/``
    (2024.4+) and/or ``.storage/brand_cache/<domain>/``. Copy to both
    locations so the integration card can show the bundled icon.
    """
    component_dir = Path(__file__).parent.resolve()
    config_path = Path(hass.config.path())

    brand_dirs = [
        config_path / ".cache" / "brands" / "integrations" / DOMAIN,
        config_path / STORAGE_DIR / "brand_cache" / DOMAIN,
    ]

    for brand_dir in brand_dirs:
        brand_dir.mkdir(parents=True, exist_ok=True)

        for filename in ("icon.png", "icon@2x.png", "logo.png"):
            source = component_dir / filename
            dest = brand_dir / filename
            if source.exists():
                try:
                    shutil.copy2(source, dest)
                    _LOGGER.debug(
                        "Copied %s to %s (%s bytes)",
                        filename,
                        brand_dir,
                        dest.stat().st_size,
                    )
                except OSError as err:
                    _LOGGER.warning(
                        "Failed to copy brand icon %s to %s: %s",
                        filename,
                        brand_dir,
                        err,
                    )
            else:
                _LOGGER.debug("Brand icon source missing: %s", source)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the lunar_sensor component."""
    await hass.async_add_executor_job(_sync_brand_icons, hass)

    @callback
    def _on_start(_):
        _sync_brand_icons(hass)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _on_start)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lunar_sensor from a config entry."""
    await hass.async_add_executor_job(_sync_brand_icons, hass)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
