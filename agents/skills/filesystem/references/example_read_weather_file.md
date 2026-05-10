# Example: Reading a Text File

**Use Case:** User asks to read a specific file like "weather.txt", "config.json", or any file with an extension.

**User Query:**
> "Read the file weather.txt"

**Correct Approach:**
```bash
python scripts/read_file.py "weather.txt"
```

**Expected Output:**
```json
{
  "success": true,
  "filepath": "C:/path/to/weather.txt",
  "content": "Sunny, 75°F...",
  "size": 256
}
```

**Key Points:**
- Always use filesystem skill for file operations, even if filename contains keywords from other skills
- File extensions (.txt, .json, .md, etc.) indicate file operations, not conceptual queries
- If file doesn't exist, the script returns `success: false` with error message
