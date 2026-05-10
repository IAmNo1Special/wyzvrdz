---
name: cron-manager
description: Schedule, manage, and audit autonomous background tasks for the Wyzvrd agent. Use when the user asks to schedule recurring tasks, set up reminders, create periodic jobs, or when they mention "cron", "schedule", "remind me", "every day", "every hour", or "periodically".
license: MIT
compatibility: Requires Wyzvrd agent with CronService running. Works with asyncio-based agent frameworks.
metadata:
  version: 0.2.0
  author: IAmNo1Special
  category: system
  tags: [cron, scheduling, automation, background-tasks]
---

# Cron Manager

## Overview

The Cron Manager gives Wyzvrd autonomous agency to schedule, manage, and audit its own proactive task lifecycle via a normalized JSON registry.

## When to use this skill

Use this skill when the user wants to:

- Schedule recurring tasks ("every hour", "daily at 9am")
- Set up one-time future tasks ("tomorrow at 3pm")
- Create randomized tasks ("sometime today", "randomly this week")
- Check status of background jobs ("is my job running?")
- Remove or cancel existing jobs

## Core Strategy

When the user asks to "remember to", "periodically", or "spontaneously" do something:

1. **Identify Schedule Type:**

   - **Fixed:** Specific date/time ("tomorrow at 3pm")
   - **Interval:** Recurring loop ("every 30 minutes")
   - **Random:** Surprise engagement ("sometime today")

1. **Schema Enforcement:** Always provide all keys. Use `null` for inactive parameters.

1. **Hydration:** For `is_random` tasks, set flags to `True` but leave targets `null`—the CronService will seed specific times.

1. **Verification:** Before adding, list existing jobs to prevent duplicates.

1. **Live Truth:** When checking status, prioritize lock files and heartbeat over registry metadata.

## Gotchas

- **Time Format:** Always use 24-hour HH:MM (e.g., "18:00" not "6 PM")
- **Date Format:** Always use ISO 8601 YYYY-MM-DD
- **Atomic Prompts:** The `prompt` must be self-contained—assume no previous context
- **Steam Deck:** Avoid intervals < 5 minutes to preserve battery
- **First Run:** Interval jobs trigger immediately on creation—warn the user if this matters
- **Job Names:** Must be unique. Check with `list` before `add`
- **Service Health:** Check `cron_service.heartbeat` before assuming the service is running

## Quick Reference

### Schedule Types

| Type         | Flags                                           | Example                   |
| ------------ | ----------------------------------------------- | ------------------------- |
| Daily fixed  | `fixed_time: "09:00"`                           | Every day at 9am          |
| One-time     | `fixed_date: "2026-04-20", fixed_time: "15:00"` | April 20 at 3pm           |
| Interval     | `interval_minutes: 30`                          | Every 30 minutes          |
| Random daily | `is_random: true`                               | Once daily at random time |
| Random date  | `is_random_date: true`                          | Random day within 30 days |

### Required Parameters

All jobs require:

- `--name`: Unique identifier (lowercase, alphanumeric + hyphens)
- `--prompt`: Self-contained instructions for the agent

Plus at least one schedule parameter.

## Workflows

### Add a Recurring Task

1. Check for existing jobs to avoid name collisions:

   ```bash
   python scripts/manage_cron.py --action list
   ```

1. Add the job with appropriate schedule:

   ```bash
   python scripts/manage_cron.py --action add \
     --name daily-backup \
     --prompt "Run database backup and verify success" \
     --fixed_time "02:00"
   ```

1. Verify the job was added:

   ```bash
   python scripts/manage_cron.py --action list
   ```

### Check Job Status

```bash
python scripts/check_cron_status.py
```

For a specific job:

```bash
python scripts/check_cron_status.py --job_name daily-backup
```

### Remove a Job

```bash
python scripts/manage_cron.py --action remove --name daily-backup
```

## Script Interface

### `scripts/manage_cron.py`

Primary CRUD interface to the registry.

**Usage:**

```bash
python scripts/manage_cron.py --action [add|list|remove] [parameters]
```

**Key Features:**

- Atomic registry updates (writes to temp file, then renames)
- Schema normalization (all fields present, null for unused)
- Built-in validation (regex for HH:MM, YYYY-MM-DD)
- JSON output to stdout for programmatic parsing

**Examples:**

Add daily recurring job:

```bash
python scripts/manage_cron.py --action add \
  --name morning-briefing \
  --prompt "Generate daily summary report" \
  --fixed_time "09:00"
```

Add interval job:

```bash
python scripts/manage_cron.py --action add \
  --name health-check \
  --prompt "Check system health" \
  --interval_minutes 30
```

Add random daily job:

```bash
python scripts/manage_cron.py --action add \
  --name random-reminder \
  --prompt "Send motivational message" \
  --is_random
```

### `scripts/check_cron_status.py`

Truth monitor for background processes.

**Usage:**

```bash
python scripts/check_cron_status.py [--job_name <name>]
```

**Exit Codes:**

- 0: Success
- 1: Registry missing
- 2: JSON parse failure
- 3: Job not found

**Checks:**

- Heartbeat verification (is service alive?)
- Lock file detection (is job running right now?)
- Registry state (last run times, schedules)

## Reference Library

See `references/` directory for specific implementation patterns:

- [add_recurring_task.md](references/add_recurring_task.md): Interval-based loops
- [schedule_fixed_briefing.md](references/schedule_fixed_briefing.md): Daily clock events
- [create_spontaneous_task.md](references/create_spontaneous_task.md): Random triggers
- [remove_existing_job.md](references/remove_existing_job.md): Safe cleanup
- [audit_system_health.md](references/audit_system_health.md): Diagnostics

## Validation Patterns

See [references/validation.md](references/validation.md) for common validation patterns and error handling.

## Output Templates

Use templates in `assets/` for consistent job execution reporting:

- [assets/output_template.md](assets/output_template.md): Standard execution report format
