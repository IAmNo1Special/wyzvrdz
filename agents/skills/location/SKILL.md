---
name: location
description: Comprehensive location and spatial context services, including user location management and manual overrides.
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Location Instructions

Use this skill whenever you need to know the user's location (for weather, time, or localized queries) or when a user corrects their current location information.

## Step 1: Determine the Current Location
Whenever a location is needed (and not explicitly provided), run the `resolve_location.py` script. This script automatically handles the hierarchy of truth: **Manual Override > IP-based Location**.

```bash
python scripts/resolve_location.py
```

## Step 2: Handle Location Corrections
If the user says "That's wrong," "I'm not there," or "My location is actually [X]":
1. **Identify the missing info**: Ask for City, State, Country, and Postal Code if not provided.
2. **Update the Override**: Run the `update_location.py` script.

```bash
python scripts/update_location.py --city "Los Angeles" --state "CA" --country "USA" --postal "90210"
```

## Available Scripts

### **`scripts/resolve_location.py`**
- **Description**: Returns the current best guess for the user's location based on manual overrides or IP detection.
- **Output**: JSON object with city, state, country, and postal code.

### **`scripts/lookup_ip.py`**
- **Description**: Fetches location information specifically from the user's current IP address.

### **`scripts/update_location.py`**
- **Description**: Sets a manual override for the user's location.
- **Usage**: `python scripts/update_location.py --city <city> --state <state> --country <country> --postal <postal>`

### **`scripts/get_postal_from_address.py`**
- **Description**: Resolves a City/State/Country into a postal code.
- **Usage**: `python scripts/get_postal_from_address.py --city <city> --state <state> --country <country>`

### **`scripts/get_info_from_postal.py`**
- **Description**: Geocodes a postal code into latitude, longitude, and country data.
- **Usage**: `python scripts/get_info_from_postal.py <postal>`

## Gotchas

- **Manual Override Priority**: If user says "I'm in Chicago", this overrides IP detection. Always update location before using it for other skills.
- **Partial Information**: User may provide only city name. Ask for state/country/postal if needed for accuracy.
- **IP Fallback**: `resolve_location.py` uses IP geolocation as fallback. Accuracy varies by VPN/proxy usage.
- **Validation**: `get_postal_from_address.py` may fail if city/state/country combination is ambiguous.
- **Timezone Awareness**: Location provides coordinates but timezone conversion requires additional calculation.
