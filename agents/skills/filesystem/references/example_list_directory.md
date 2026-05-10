# Example: Listing Directory Contents

**Use Case:** User asks what's in a folder, to list files, or see directory contents.

**User Query:**

> "List all files in the current directory"
> "What files are in ./documents?"

**Correct Approach:**

```bash
python scripts/list_directory.py
# Or for a specific path:
python scripts/list_directory.py "./documents"
```

**Expected Output:**

```json
{
  "success": true,
  "path": "C:/path/to/current/dir",
  "items": [
    {"name": "weather.txt", "type": "file", "path": "..."},
    {"name": "data", "type": "directory", "path": "..."},
    {"name": "config.json", "type": "file", "path": "..."}
  ],
  "count": 3
}
```

**Key Points:**

- Default path is current directory (.) if not specified
- Shows both files and directories with their types
- Full paths are included for each item
