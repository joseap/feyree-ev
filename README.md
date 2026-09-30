# feyree-ev

Home Assistant custom integration for Feyree EV chargers (monophase).

## Features

- Voltage, current, power, temperature monitoring
- Session energy tracking
- Charge enable/disable control
- Current preset and max configuration
- **Auto IP discovery** when connection lost

## DPS Mapping (Monophase)

| DPS | Type | Name | Unit | Scale |
|-----|------|------|------|-------|
| 101 | Enum | Charging state | 0-6 | - |
| 102 | Integer | Voltage | 0-2500 (×0.1V) | V |
| 105 | Integer | Current | 0-320 (×0.1A) | A |
| 109 | Integer | Power | 0-7000 (×0.1kW) | kW |
| 110 | Integer | Temperature | 0-100 (×0.1°C) | °C |
| 112 | Integer | Session Energy | 0-100000 (×0.1kWh) | kWh |
| 115 | Integer | Current Preset | 6-32A | A |
| 124 | Boolean | Charge Enable | on/off | - |
| 125 | Integer | Current Max | 6-32A | A |
| 10 | Raw | Fault Code | hex | - |

## Installation

1. Copy `custom_components/feyree_ev` to your HA `config/custom_components/`
2. Restart Home Assistant
3. Add integration via UI

## Configuration

- **Device ID**: Your Tuya device ID (e.g. `bfd76e9136036339b6wp8k`)
- **Device IP**: Local IP of the charger (auto-discovered on change)
- **Local Key**: Tuya local key
- **Version**: 3.5
