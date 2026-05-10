---
name: filesystem
description: Read, write, and manage files on the local filesystem. Use when the user asks to read a file, write to a file, list directory contents, check if a file exists, or perform any file operations.
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Filesystem Skill

This skill provides file operation capabilities. Use it for all file-related requests.

## When to Use

Use this skill when the user asks for:
- Reading files: "read file.txt", "show me the contents of..."
- Writing files: "write to file.txt", "save this as...", "create a file"
- Listing directories: "list files in...", "what's in the folder"
- Checking file existence: "does file.txt exist?"
- File paths mentioned explicitly: "open weather.txt", "read config.json"

## Available Scripts

### `scripts/read_file.py`

Read the contents of a file.

**Usage:**
```bash
python scripts/read_file.py <filepath>
```

**Examples:**
```bash
python scripts/read_file.py "weather.txt"
python scripts/read_file.py "/path/to/config.json"
```

### `scripts/write_file.py`

Write content to a file (creates or overwrites).

**Usage:**
```bash
python scripts/write_file.py <filepath> <content>
```

**Examples:**
```bash
python scripts/write_file.py "output.txt" "Hello World"
python scripts/write_file.py "data.json" '{"key": "value"}'
```

### `scripts/list_directory.py`

List contents of a directory.

**Usage:**
```bash
python scripts/list_directory.py [path]
```

**Examples:**
```bash
python scripts/list_directory.py
python scripts/list_directory.py "./documents"
```

### `scripts/file_exists.py`

Check if a file or directory exists.

**Usage:**
```bash
python scripts/file_exists.py <filepath>
```

**Examples:**
```bash
python scripts/file_exists.py "config.txt"
```

### `scripts/copy_file.py`

Copy a file from source to destination.

**Usage:**
```bash
python scripts/copy_file.py <source> <destination>
```

**Examples:**
```bash
python scripts/copy_file.py "original.txt" "backup/original.txt"
python scripts/copy_file.py "config.json" "config.json.bak"
```

### `scripts/delete_file.py`

Delete a file or directory.

**Usage:**
```bash
python scripts/delete_file.py <filepath> [--recursive]
```

**Examples:**
```bash
python scripts/delete_file.py "temp.txt"
python scripts/delete_file.py "old_folder" --recursive
```

### `scripts/search_files.py`

Search for files by name pattern or content.

**Usage:**
```bash
python scripts/search_files.py [directory] --pattern "*.py"
python scripts/search_files.py [directory] --content "search term"
```

**Examples:**
```bash
python scripts/search_files.py . --pattern "*.json"
python scripts/search_files.py . --content "TODO" --extensions ".py,.md"
```

### `scripts/file_info.py`

Get detailed information about a file or directory (size, type, permissions, timestamps).

**Usage:**
```bash
python scripts/file_info.py <filepath>
```

**Examples:**
```bash
python scripts/file_info.py "document.pdf"
python scripts/file_info.py "data_folder"
```

## Common Patterns

1. **Reading a specific file**: "Read weather.txt" -> Use `read_file.py`
2. **Writing output**: "Save this to results.txt" -> Use `write_file.py`
3. **Listing files**: "What files are in this directory?" -> Use `list_directory.py`
4. **Checking existence**: "Does config.json exist?" -> Use `file_exists.py`
5. **Copying files**: "Backup config.json" -> Use `copy_file.py`
6. **Deleting files**: "Remove temp.txt" -> Use `delete_file.py`
7. **Searching files**: "Find all Python files" -> Use `search_files.py`
8. **File metadata**: "How big is data.csv?" -> Use `file_info.py`

## Important Notes

- Always use the filesystem skill for file operations, even if the filename contains keywords from other skills (e.g., "weather.txt" is a file, not a weather query)
- File paths can be relative ("./file.txt") or absolute ("/full/path/file.txt")
- If no path is specified, assume the current working directory

## Gotchas

- **Path traversal blocked**: Scripts reject paths that escape the base directory (e.g., `../../../etc/passwd`). Always use paths within the workspace.
- **Binary files**: `read_file.py` returns text content; binary files may show garbled output. Check file type first if uncertain.
- **Large files**: Files >10MB may cause memory issues. Consider chunking or streaming for very large files.
- **Encoding**: UTF-8 is assumed. Files with BOM or other encodings may have garbled first characters.
- **Concurrent access**: Multiple processes may conflict when writing the same file. Use file locking for critical operations.
- **Path resolution**: Relative paths resolve from the skill's assets directory. Use absolute paths for clarity when needed.

## Need Help? Check the Examples

If you're unsure how to handle a specific file operation scenario, look at the example files in the `references/` directory:

- `references/example_read_weather_file.md` - Reading text/config files
- `references/example_write_output_file.md` - Writing/saving content
- `references/example_list_directory.md` - Listing directory contents
- `references/example_check_file_exists.md` - Checking file existence
- `references/example_discord_json_file.md` - Avoiding false positives (file vs skill keywords)
- `references/example_multi_step_workflow.md` - Complex file operations

Each example shows the user query, correct script usage, expected output, and key decision points.
