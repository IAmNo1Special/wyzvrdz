# Validation Patterns for Cron Manager

This document provides reusable validation patterns and error handling strategies for cron job management.

## Time Format Validation

### Pattern: HH:MM (24-hour)

**Regex:** `^\d{2}:\d{2}$`

**Valid examples:**
- `00:00` (midnight)
- `09:30` (9:30 AM)
- `23:59` (11:59 PM)

**Invalid examples:**
- `9:30` (missing leading zero)
- `25:00` (hour > 23)
- `12:30 PM` (contains AM/PM)

**Python implementation:**
```python
def validate_time(time_str: str) -> bool:
    if not time_str:
        return True  # Optional field
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        return False
    hour, minute = map(int, time_str.split(":"))
    return 0 <= hour <= 23 and 0 <= minute <= 59
```

## Date Format Validation

### Pattern: ISO 8601 (YYYY-MM-DD)

**Valid examples:**
- `2026-04-19`
- `2025-12-31`

**Invalid examples:**
- `04-19-2026` (US format)
- `19/04/2026` (European format)
- `2026-4-9` (single digits)

**Python implementation:**
```python
def validate_date(date_str: str) -> bool:
    if not date_str:
        return True  # Optional field
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
```

## Job Name Validation

### Rules
- 1-64 characters
- Lowercase alphanumeric and hyphens only
- Must not start or end with hyphen
- Must not contain consecutive hyphens
- Must be unique in registry

**Python implementation:**
```python
def validate_job_name(name: str, existing_names: list[str]) -> tuple[bool, str]:
    if not name:
        return False, "Job name is required"

    if len(name) > 64:
        return False, "Job name must be 64 characters or less"

    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, "Job name must be lowercase alphanumeric with hyphens"

    if name in existing_names:
        return False, f"Job '{name}' already exists"

    return True, ""
```

## Schema Validation

### Required Fields

Every job must have:
- `name` (string, validated above)
- `prompt` (string, non-empty)
- At least one schedule parameter

### Schedule Parameter Validation

At least one of:
- `fixed_date` (YYYY-MM-DD)
- `fixed_time` (HH:MM)
- `interval_minutes` (positive integer)
- `interval_hours` (positive integer)
- `interval_days` (positive integer)
- `interval_weeks` (positive integer)
- `interval_months` (positive integer)
- `interval_years` (positive integer)
- `is_random` (boolean)
- `is_random_date` (boolean)

**Python implementation:**
```python
def has_schedule(job: dict) -> bool:
    schedule_fields = [
        'fixed_date', 'fixed_time', 'interval_minutes',
        'interval_hours', 'interval_days', 'interval_weeks',
        'interval_months', 'interval_years', 'is_random',
        'is_random_date'
    ]
    return any(job.get(field) for field in schedule_fields)
```

## Error Handling Patterns

### Pattern: Structured Error Response

All scripts should return consistent JSON error responses:

```python
{
    "status": "error",
    "message": "Human-readable error description",
    "data": {
        "field": "Which field caused the error",
        "code": "ERROR_CODE_FOR_PROGRAMMATIC_HANDLING"
    }
}
```

### Pattern: Graceful Degradation

When checking status, handle missing files gracefully:

```python
def get_heartbeat() -> dict:
    if not HEARTBEAT_FILE.exists():
        return {
            "status": "OFFLINE",
            "message": "No heartbeat found - service may not be running"
        }
    # ... read and parse
```

### Pattern: Atomic Operations

Always write to temp file, then rename:

```python
def atomic_write(data: dict, filepath: Path):
    tmp_file = filepath.with_suffix('.tmp')
    try:
        with open(tmp_file, 'w') as f:
            json.dump(data, f, indent=4)
        tmp_file.replace(filepath)
    except Exception:
        if tmp_file.exists():
            tmp_file.unlink()
        raise
```

## Exit Codes

Use consistent exit codes:

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | Operation completed successfully |
| 1 | Validation error | Invalid input, missing required fields, duplicates |
| 2 | File I/O error | Cannot read/write registry, permission denied |
| 3 | Not found | Job not found, resource missing |

## Logging Patterns

### Structured Logging

Use JSON format for machine parsing:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        })
```

### Progressive Detail

- **ERROR**: Something failed, action required
- **WARNING**: Unexpected but handled
- **INFO**: Normal operation milestones
- **DEBUG**: Detailed execution flow

## Common Validation Checklist

When adding a job, verify:

- [ ] Name is valid (format, uniqueness)
- [ ] Prompt is non-empty and self-contained
- [ ] At least one schedule parameter provided
- [ ] Time format is HH:MM (if provided)
- [ ] Date format is YYYY-MM-DD (if provided)
- [ ] Intervals are positive integers (if provided)
- [ ] No conflicting schedule types

When checking status, verify:

- [ ] Registry file exists
- [ ] Registry is valid JSON
- [ ] Heartbeat is recent (< 60 seconds)
- [ ] Lock files correspond to active jobs
- [ ] No orphaned lock files (stale > 1 hour)

## Testing Validation

### Unit Test Examples

```python
def test_validate_time():
    assert validate_time("09:00") is True
    assert validate_time("25:00") is False
    assert validate_time("9:00") is False
    assert validate_time("") is True  # Optional

def test_has_schedule():
    assert has_schedule({"fixed_time": "09:00"}) is True
    assert has_schedule({"is_random": True}) is True
    assert has_schedule({"name": "test"}) is False
```
