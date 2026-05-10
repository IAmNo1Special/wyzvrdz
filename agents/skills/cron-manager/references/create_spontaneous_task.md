# Example: Randomized Proactive Engagement

**User Intent:** "Surprise me with a random tech tip once a day."

**Reasoning:** The user wants spontaneity. I should set `is_random` to true and leave `random_target_time` and `last_run` as null for the system to hydrate.

**Execution:**

```bash
python scripts/manage_cron.py --action add \
  --name "Spontaneous Tech Tip" \
  --prompt "Select a random Python file. Explain a complex function as a 'Tech Tip' in the chat log." \
  --is_random True
```
