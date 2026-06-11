"""农历传感器 - 提供农历日期、节日、节气三个实体"""
from datetime import date, timedelta

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util.dt import now

from lunar_python import Lunar, Solar

DOMAIN = "lunar_sensor"

SENSOR_DESCRIPTIONS = (
    SensorEntityDescription(
        key="date",
        name="农历日期",
        icon="mdi:calendar-month",
    ),
    SensorEntityDescription(
        key="festival",
        name="农历节日",
        icon="mdi:calendar-star",
    ),
    SensorEntityDescription(
        key="term",
        name="节气",
        icon="mdi:leaf",
    ),
)


def _get_lunar_data(today: date | None = None) -> dict:
    """获取当天的农历日期、节日和节气数据。"""
    today = today or now().date()
    solar = Solar(today.year, today.month, today.day, 0, 0, 0)
    lunar = Lunar.fromSolar(solar)

    festivals = lunar.getFestivals()
    festival = ""
    if festivals:
        festival = festivals[0]
        if len(festival) > 2 and festival.endswith("节"):
            festival = festival[:-1]

    return {
        "date": f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        "festival": festival,
        "term": lunar.getJieQi() or "",
    }


def _build_device_info() -> DeviceInfo:
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
    data = _get_lunar_data()
    entities = [
        LunarSensor(description, device_info, data)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities, update_before_add=True)

    @callback
    async def _async_update(_):
        """每分钟检查一次，数据变化时更新。"""
        new_data = _get_lunar_data()
        for entity in entities:
            entity.update_data(new_data)

    async_track_time_interval(hass, _async_update, timedelta(minutes=1))


class LunarSensor(SensorEntity):
    """农历传感器通用实体。"""

    def __init__(self, description: SensorEntityDescription, device_info: DeviceInfo, data: dict):
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = f"lunar_sensor_{description.key}"
        self._data = data

    @property
    def native_value(self):
        return self._data.get(self.entity_description.key, "")

    def update_data(self, data: dict) -> None:
        """更新数据，只有值变化时才写入状态。"""
        new_value = data.get(self.entity_description.key, "")
        if self.native_value == new_value:
            return
        self._data = data
        self.async_write_ha_state()
