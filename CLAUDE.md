# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration distributed via HACS. It provides three sensors that expose Chinese lunar calendar data (农历日期, 农历节日, 二十四节气) using the `lunar-python` library.

## Architecture

The integration follows the standard Home Assistant custom component structure under `custom_components/lunar_sensor/`:

- **`__init__.py`** — Entry point. Implements `async_setup_entry` / `async_unload_entry` and forwards setup to the `sensor` platform.
- **`sensor.py`** — Contains all three sensor entities: `LunarDateSensor`, `LunarFestivalSensor`, `SolarTermSensor`. All extend `SensorEntity` and call `date.today()` + `Lunar.fromSolar()` on each update. Entities are registered with `async_add_entities(..., update_before_add=True)` and refreshed hourly via `async_track_time_interval`.
- **`config_flow.py`** — Config flow handler (`LunarSensorConfigFlow`). The UI setup requires no user input; submitting creates a single config entry titled "农历传感器".
- **`manifest.json`** — Declares `domain: lunar_sensor`, dependency `lunar-python`, `config_flow: true`, and `iot_class: local_polling`.
- **`strings.json`** — Chinese UI strings for the config flow.

### Key Implementation Detail: Festival Name Normalization

`LunarFestivalSensor.update()` strips a trailing "节" character from festival names **only when the resulting string would be longer than 2 characters**. Two-character festivals like "春节" are left unchanged. This logic lives in `sensor.py:68-69`.

### External Dependency

All sensors rely on the `lunar-python` package (declared in `manifest.json`). It provides the `Solar` → `Lunar` conversion and methods like `getMonthInChinese()`, `getDayInChinese()`, `getFestivals()`, and `getJieQi()`.

## Development Notes

- There is **no test suite**, **no linting configuration**, and **no build tooling** (e.g., no `pyproject.toml`, `setup.py`, `Makefile`, `tox.ini`, or pre-commit hooks).
- To validate changes, you can run the Home Assistant development environment or install the integration in a running HA instance and check the logs.
- The code is in Chinese (Simplified) and should remain so for user-facing strings.
- When adding new sensors or modifying existing ones, keep the pattern of calling `date.today()` → `Solar(...)` → `Lunar.fromSolar(...)` inside the `update()` method.
