# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Home Assistant custom integration (`lunar_sensor`) that provides three sensors for lunar calendar information: lunar date (农历日期), lunar festival (农历节日), and solar term (节气). It is distributed via HACS (Home Assistant Community Store).

The integration uses the [`lunar-python`](https://pypi.org/project/lunar-python/) library to perform calendar conversions and is configured via UI (config flow) — no YAML required.

## Repository Structure

```
ha-lunar-sensor/
├── custom_components/lunar_sensor/   # Integration code
│   ├── __init__.py                   # Setup, brand icon sync
│   ├── config_flow.py                # UI configuration flow
│   ├── sensor.py                     # Three SensorEntity implementations
│   ├── manifest.json                 # Integration metadata
│   ├── strings.json                  # English UI strings
│   ├── translations/zh.json          # Chinese UI strings
│   ├── icon.png / icon@2x.png        # HACS/HA brand icons
│   └── logo.png
├── hacs.json                         # HACS metadata
└── README.md
```

## Architecture

### Integration Lifecycle

1. **`manifest.json`** declares `config_flow: true`, so Home Assistant loads the integration via UI.
2. **`config_flow.py`** — `LunarSensorConfigFlow` handles the config flow. It has no user-configurable fields (empty schema); submitting immediately creates a config entry titled "农历传感器".
3. **`__init__.py`** — `async_setup_entry` forwards to the `sensor` platform and triggers brand-icon syncing.
4. **`sensor.py`** — `async_setup_entry` creates three `SensorEntity` instances sharing a single `DeviceInfo` object, then registers an hourly `async_track_time_interval` update.

### Brand Icon Sync (`__init__.py`)

Home Assistant caches brand icons under `<config>/.cache/brands/integrations/<domain>/` and/or `<config>/.storage/brand_cache/<domain>/`. On startup, `_sync_brand_icons` copies the bundled `icon.png`, `icon@2x.png`, and `logo.png` into both locations so the integration card displays correctly.

### Sensor Entities (`sensor.py`)

All three sensors share one `DeviceInfo` (identifier: `(DOMAIN, "lunar_sensor_device")`) and update hourly:

| Entity Class | Unique ID | Icon | Description |
|--------------|-----------|------|-------------|
| `LunarDateSensor` | `lunar_sensor_date` | `mdi:calendar-month` | Lunar date string, e.g. "四月廿五" |
| `LunarFestivalSensor` | `lunar_sensor_festival` | `mdi:calendar-star` | Festival name with trailing "节" stripped when >2 chars |
| `SolarTermSensor` | `lunar_sensor_term` | `mdi:leaf` | 24 solar term name, e.g. "芒种" |

All conversion logic uses `lunar_python.Solar` → `Lunar.fromSolar()`.

## Development Commands

### Local Python Testing

The integration has no formal test suite in-repo. For ad-hoc verification of `lunar-python` logic:

```bash
# Ensure lunar-python is installed
pip install lunar-python

# Quick smoke test of the conversion logic
python -c "
from datetime import date
from lunar_python import Lunar, Solar
today = date.today()
solar = Solar(today.year, today.month, today.day, 0, 0, 0)
lunar = Lunar.fromSolar(solar)
print(f'Date: {lunar.getMonthInChinese()}月{lunar.getDayInChinese()}')
print(f'Festivals: {lunar.getFestivals()}')
print(f'Term: {lunar.getJieQi()}')
"
```

### Lint / Type Check

No project-level linter config is present. If adding one, target Python 3.11+ (matching Home Assistant's runtime). Recommended tools:

```bash
ruff check custom_components/
ruff format custom_components/
```

### Validate for Home Assistant

Use the official `homeassistant` dev container or `hassfest` to validate manifests and translations:

```bash
# If running inside a Home Assistant core dev environment
python -m script.hassfest
```

Or via the VS Code devcontainer provided by the Home Assistant add-on/frontend repositories.

### HACS Validation

```bash
# Requires HACS action or CLI (if available in CI)
# Typical action in .github/workflows/validate.yml:
# - uses: hacs/action@main
#   with:
#     category: integration
```

## Key Conventions

- **Domain**: `lunar_sensor` — used as folder name, manifest domain, config entry title, and device identifier prefix.
- **Single-instance restriction**: The config flow does not currently enforce a single instance, but `strings.json` defines `single_instance_allowed` for future use.
- **Translations**: `strings.json` is the fallback; `translations/zh.json` provides Chinese UI text. Keep them in sync.
- **No YAML configuration**: The integration is UI-only (`config_flow: true`). Do not add `async_setup_platform` or platform YAML schemas.
- **Version bumping**: Update `manifest.json` → `version` and `sensor.py` → `sw_version` together when releasing.

## Release Checklist

1. Bump version in `manifest.json` and `sensor.py` (`sw_version`).
2. Ensure `strings.json` and `translations/zh.json` are synchronized.
3. Verify brand icons (`icon.png`, `icon@2x.png`, `logo.png`) are present.
4. Tag the release: `git tag vX.Y.Z && git push origin vX.Y.Z`.
5. HACS will pick up the new tag automatically.
