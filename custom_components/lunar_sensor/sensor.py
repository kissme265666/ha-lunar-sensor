"""农历传感器 - 提供农历日期、节日、节气三个实体"""
from datetime import date, timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import callback, HomeAssistant
from homeassistant.config_entries import ConfigEntry

from lunar_python import Lunar, Solar

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lunar_sensor"


def _build_device_info() -> DeviceInfo:
    """Build shared DeviceInfo for all sensors."""
    return DeviceInfo(
        identifiers={(DOMAIN, "lunar_sensor_device")},
        name="农历传感器",
        manufacturer="Lunar Python",
        model="农历日期传感器",
        sw_version="1.0.0",
    )


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up sensors from a config entry."""
    device_info = _build_device_info()

    sensors = [
        LunarDateSensor(device_info),
        LunarFestivalSensor(device_info),
        SolarTermSensor(device_info),
    ]

    async_add_entities(sensors, update_before_add=True)

    @callback
    async def update_sensors(_):
        """每小时更新一次"""
        for sensor in sensors:
            sensor.update()
            sensor.async_write_ha_state()

    async_track_time_interval(hass, update_sensors, timedelta(hours=1))


class LunarDateSensor(SensorEntity):
    """农历日期传感器，如'四月廿五'"""

    def __init__(self, device_info: DeviceInfo):
        self._attr_name = "农历日期"
        self._attr_unique_id = "lunar_sensor_date"
        self._attr_icon = "mdi:calendar-month"
        self._attr_device_info = device_info

    def update(self):
        today = date.today()
        solar = Solar(today.year, today.month, today.day, 0, 0, 0)
        lunar = Lunar.fromSolar(solar)
        self._attr_native_value = f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"


class LunarFestivalSensor(SensorEntity):
    """农历节日传感器，如'端午'（两字，去掉末尾'节'）"""

    def __init__(self, device_info: DeviceInfo):
        self._attr_name = "农历节日"
        self._attr_unique_id = "lunar_sensor_festival"
        self._attr_icon = "mdi:calendar-star"
        self._attr_device_info = device_info

    def update(self):
        today = date.today()
        solar = Solar(today.year, today.month, today.day, 0, 0, 0)
        lunar = Lunar.fromSolar(solar)
        festivals = lunar.getFestivals()

        if festivals:
            raw = festivals[0]
            if len(raw) > 2 and raw.endswith("节"):
                raw = raw[:-1]
            self._attr_native_value = raw
        else:
            self._attr_native_value = ""


class SolarTermSensor(SensorEntity):
    """节气传感器，如'芒种'"""

    def __init__(self, device_info: DeviceInfo):
        self._attr_name = "节气"
        self._attr_unique_id = "lunar_sensor_term"
        self._attr_icon = "mdi:leaf"
        self._attr_device_info = device_info

    def update(self):
        today = date.today()
        solar = Solar(today.year, today.month, today.day, 0, 0, 0)
        lunar = Lunar.fromSolar(solar)
        term = lunar.getJieQi()
        self._attr_native_value = term if term else ""
