"""农历传感器 - 提供农历日期、节日、节气三个实体"""
from datetime import date, timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.core import callback

from lunar_python import Lunar, Solar

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lunar_sensor"


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """设置传感器平台"""
    sensors = [
        LunarDateSensor(),
        LunarFestivalSensor(),
        SolarTermSensor(),
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

    def __init__(self):
        self._attr_name = "农历日期"
        self._attr_unique_id = "lunar_sensor_date"
        self._attr_icon = "mdi:calendar-month"

    def update(self):
        today = date.today()
        solar = Solar(today.year, today.month, today.day, 0, 0, 0)
        lunar = Lunar.fromSolar(solar)
        self._attr_native_value = f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"


class LunarFestivalSensor(SensorEntity):
    """农历节日传感器，如'端午'（两字，去掉末尾'节'）"""

    def __init__(self):
        self._attr_name = "农历节日"
        self._attr_unique_id = "lunar_sensor_festival"
        self._attr_icon = "mdi:lantern"

    def update(self):
        today = date.today()
        solar = Solar(today.year, today.month, today.day, 0, 0, 0)
        lunar = Lunar.fromSolar(solar)
        festivals = lunar.getFestivals()

        if festivals:
            raw = festivals[0]
            # 去掉末尾"节"字，但保留两字节日（如春节）
            if len(raw) > 2 and raw.endswith("节"):
                raw = raw[:-1]
            self._attr_native_value = raw
        else:
            self._attr_native_value = ""


class SolarTermSensor(SensorEntity):
    """节气传感器，如'芒种'"""

    def __init__(self):
        self._attr_name = "节气"
        self._attr_unique_id = "lunar_sensor_term"
        self._attr_icon = "mdi:weather-partly-snowy-rainy"

    def update(self):
        today = date.today()
        solar = Solar(today.year, today.month, today.day, 0, 0, 0)
        lunar = Lunar.fromSolar(solar)
        term = lunar.getJieQi()
        self._attr_native_value = term if term else ""
