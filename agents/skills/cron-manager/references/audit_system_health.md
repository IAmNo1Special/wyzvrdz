# Example: Auditing System Health & Troubleshooting

**User Intent:** "Check if my scheduled backups are actually running and tell me when the next one is."

**Reasoning:** The user is asking for a status update. I should run the health check script to see the `last_run` timestamps and the `Next Run In` countdowns.

**Execution:**

```bash
python scripts/check_cron_status.py
```

**Expected Output:**

A table showing all jobs, their status, and when they will run next. This helps verify that the system is healthy and that scheduled tasks are properly registered and timed.
