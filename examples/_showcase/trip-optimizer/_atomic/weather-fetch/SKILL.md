---
name: weather-fetch
description: Fetch historical weather data and forecasts for a location and date range.
level: 1
operation: READ
license: Apache-2.0
---

# Weather Fetch

A Level 1 atomic skill that retrieves weather data for trip planning.

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | City or coordinates |
| `start_date` | string | Yes | Start of date range |
| `end_date` | string | Yes | End of date range |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `avg_temperature` | number | Average temp in Fahrenheit |
| `sunshine_probability` | number | Chance of sunny days (0-1) |
| `rain_probability` | number | Chance of rain (0-1) |
| `daily_forecast` | list | Day-by-day breakdown |

## Example

```
weather-fetch("Puerto Vallarta", "2024-03-15", "2024-03-22"):

RETURN:
  avg_temperature: 78
  sunshine_probability: 0.92
  rain_probability: 0.05
  daily_forecast: [...]
```
