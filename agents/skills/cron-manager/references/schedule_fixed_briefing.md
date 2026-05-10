# Example: Fixed Daily Schedule

**User Intent:** "Give me a summary of my coding progress every day at 6 PM."

**Reasoning:** This is a time-specific daily task. I must use `fixed_time` in 24-hour format.

**Execution:**

```bash
python scripts/manage_cron.py --action add \
  --name "Evening Progress Report" \
  --prompt "Review git commits and file changes in the wyzvrdz repository from the last 24 hours. Summarize achievements and blockers." \
  --fixed_time "18:00"
```
