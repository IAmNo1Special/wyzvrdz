---
name: time
description: "Use when the user asks for the current time, today's date, the current timestamp, any real-time temporal information, or when the user or you need to wait, pause, or delay for a specified duration. Triggers on queries like 'what time is it', 'what's today's date', 'wait 30 seconds', 'pause for 5 minutes', or when any task requires knowing the precise current moment or blocking for a period. Do NOT use for general time-related questions like 'how many hours in a day' or time math like 'what is 3pm + 2 hours'. Wait vs Scheduling: 'Wait 30 seconds' uses this skill, 'Remind me in 2 hours' is scheduling — use a scheduling skill (e.g., cron-manager) if available."
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Time Skill

Provides real-time date/timestamp information and timed waiting.

## When to Use

Use this skill whenever:

- The user needs to know the **current** time or date
- The user or you need to **wait** for a duration. This includes:
  - "wait..."
  - "hold..."
  - "pause..."
  - "hold on..."
  - "give me a moment"
  - "hold your horses"

**Examples:**

- "What time is it?"
- "What's today's date?"
- "Give me the current timestamp"
- "Wait 30 seconds then continue"
- "Pause for 5 minutes"
- Any task that depends on knowing the precise current moment or blocking for a period

## Get the Current Timestamp

Run the `get_current_timestamp.py` script:

```bash
python scripts/get_current_timestamp.py
```

**Output**: JSON with `status`, `message`, and `data.timestamp` in `YYYY-MM-DD HH:MM:SS` format (local system time).

## Wait for a Duration

When the user needs to pause or delay, run the `wait.py` script:

```bash
python scripts/wait.py <duration>
```

**Duration formats**:

- Plain number → seconds: `30` = 30 seconds
- `s` suffix → seconds: `30s` = 30 seconds
- `m` suffix → minutes: `5m` = 5 minutes (300 seconds)
- `h` suffix → hours: `1h` = 1 hour (3600 seconds)

**Output**: JSON with `status`, `message`, and `data.waited_seconds`.

## Available Scripts

### **`scripts/get_current_timestamp.py`**

- **Description**: Returns the current date and time in `YYYY-MM-DD HH:MM:SS` format.
- **Output**: JSON object with `status`, `message`, and `data.timestamp`.
- **No arguments required**.

### **`scripts/wait.py`**

- **Description**: Blocks execution for a specified duration.
- **Usage**: `python scripts/wait.py <duration>`
- **Duration**: Supports plain seconds, or suffixed (`30s`, `5m`, `1h`).
- **Safety limit**: Maximum 1 hour. For longer delays, use a cron/scheduler skill.

## Gotchas

- **System Time**: The timestamp reflects the system's local clock. If the user needs a specific timezone, use the location skill to resolve their timezone first.
- **Not for Time Math**: "What is 3pm + 2 hours?" is arithmetic — answer directly, don't use this skill.
- **Not for General Knowledge**: "How many seconds in a year?" is general knowledge — answer directly.
- **Precision**: Returns seconds-level precision (`HH:MM:SS`), not milliseconds.
- **Wait Blocks Execution**: `wait.py` is a synchronous block — the agent cannot do anything else while waiting. Use only when the user explicitly wants to pause.
- **1-Hour Safety Cap**: `wait.py` rejects durations over 3600 seconds. For longer waits, use the cron-manager skill to schedule a future action instead.
- **Wait ≠ Scheduling**: "Wait 30 seconds" uses this skill. "Remind me in 2 hours" is scheduling — use cron-manager.
