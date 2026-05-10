# Example: Adding a Recurring Interval Task

**User Intent:** "Check for broken links in the compendium every 2 hours."

**Reasoning:** The user wants a repetitive task based on an interval. I should use `interval_hours`.

**Execution:**

```bash
python scripts/manage_cron.py --action add \
  --name "Compendium Link Audit" \
  --prompt "Scan the local compendium directory. Identify markdown links pointing to non-existent files. Log findings to logs/link_audit.md." \
  --interval_hours 2
```
