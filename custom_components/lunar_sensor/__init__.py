"""农历传感器自定义集成"""
import logging
from pathlib import Path
import shutil

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lunar_sensor"
BRAND_ICONS = ("icon.png", "icon@2x.png", "logo.png")


def _sync_brand_icons(hass: HomeAssistant) -> None:
    """将集成的图标/Logo复制到HA品牌缓存目录。"""
    component_dir = Path(__file__).parent.resolve()
    brand_dir = Path(hass.config.path()) / ".cache" / "brands" / "integrations" / DOMAIN
    brand_dir.mkdir(parents=True, exist_ok=True)

    for filename in BRAND_ICONS:
        source = component_dir / filename
        dest = brand_dir / filename
        if not source.exists():
            continue
        try:
            shutil.copy2(source, dest)
            _LOGGER.debug("已复制品牌图标 %s", filename)
        except OSError as err:
            _LOGGER.warning("复制品牌图标 %s 失败: %s", filename, err)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the lunar_sensor component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up lunar_sensor from a config entry."""
    await hass.async_add_executor_job(_sync_brand_icons, hass)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
