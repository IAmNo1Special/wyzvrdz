# Example: File vs Skill Keywords (Avoiding False Positives)

**Use Case:** Filename contains keywords that might trigger other skills.

**User Query:**
> "Read discord_config.json"
> "Show me the weather.csv file"

**Common Mistake:**
Thinking "discord" -> use discord_mgmt_agent
Thinking "weather" -> use weather skill

**Correct Approach:**
The presence of a file extension (.json, .csv, .txt, .md) indicates a **file operation**, not a conceptual query.

```bash
python scripts/read_file.py "discord_config.json"
python scripts/read_file.py "weather.csv"
```

**Key Points:**
- File extensions (.json, .csv, .txt, .md, .yaml, etc.) = filesystem skill
- Conceptual queries without file extensions = relevant skill (discord, weather, etc.)
- When in doubt: If the user mentions a filepath, use filesystem skill
