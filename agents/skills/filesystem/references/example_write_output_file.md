# Example: Writing Content to a File

**Use Case:** User asks to save content, create a file, or write output to disk.

**User Query:**

> "Write 'Hello World' to output.txt"

**Correct Approach:**

```bash
python scripts/write_file.py "output.txt" "Hello World"
```

**Expected Output:**

```json
{
  "success": true,
  "filepath": "C:/path/to/output.txt",
  "size": 11,
  "message": "Successfully wrote to output.txt"
}
```

**Key Points:**

- Creates parent directories automatically if they don't exist
- Overwrites existing files (use with caution)
- For JSON content, escape quotes properly: `'{"key": "value"}'`
