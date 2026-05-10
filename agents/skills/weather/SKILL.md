---
name: weather
description: Fetch current weather and forecast information. Use ONLY when the user asks about weather conditions, forecasts, temperature, rain, etc. Do NOT use for file operations (e.g., "read weather.txt") - those should use file tools.
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Weather Skill

Use this skill to retrieve current weather conditions and forecasts. It routes requests to the National Weather Service (NWS) for US locations or wttr.in for international ones.

**When to use**: User asks about weather, temperature, forecast, rain, snow, wind, or if they need an umbrella.
**When NOT to use**: User mentions a filename with "weather" in it (e.g., "read weather.txt", "write to weather.log") - use file tools instead.

## Available Scripts

### **`scripts/fetch_weather.py`**

- **Description**: Fetches the current weather for a specific postal or zip code.
- **Usage**: `python scripts/fetch_weather.py <postal_code>`
- **Output**: JSON object with status, message, and weather data.

### **`scripts/resolve_nws_url.py`**

- **Description**: Resolves a specific latitude and longitude to a National Weather Service (NWS) forecast endpoint.
- **Usage**: `python scripts/resolve_nws_url.py <lat> <lon>`
- **Output**: JSON object with the forecast URL.

## Workflows

### 1. Get Weather by Postal Code

If a user asks for the weather and you have their postal code:

```bash
python scripts/fetch_weather.py "90210"
```

### 2. Manual NWS Endpoint Resolution (US Only)

If you need to find the specific NWS forecast URL for coordinates:

```bash
python scripts/resolve_nws_url.py 34.0522 -118.2437
```

## Gotchas

- **File vs Weather**: "weather.txt" is a file, not a weather query. Always use filesystem skill for file operations.
- **Location Required**: `fetch_weather.py` requires a postal code. Use `location` skill first if you don't have one.
- **US Only NWS**: `resolve_nws_url.py` only works for US locations via National Weather Service.
- **International**: For non-US locations, wttr.in is used automatically via `fetch_weather.py`.
- **API Limits**: NWS has rate limits. Avoid excessive polling in tight loops.
