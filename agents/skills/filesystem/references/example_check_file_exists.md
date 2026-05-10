# Example: Checking if a File Exists

**Use Case:** User asks whether a specific file or directory exists.

**User Query:**
> "Does config.json exist?"
> "Is there a file called data.txt?"

**Correct Approach:**

```bash
python scripts/file_exists.py "config.json"
```

**Expected Output (file exists):**

```json
{
  "success": true,
  "filepath": "C:/path/to/config.json",
  "exists": true,
  "type": "file"
}
```

**Expected Output (file does not exist):**

```json
{
  "success": true,
  "filepath": "C:/path/to/config.json",
  "exists": false
}
```

**Key Points:**

- Returns `exists: true/false` to indicate presence
- Includes file type (file/directory) when it exists
- Use before read/write operations to verify file state
