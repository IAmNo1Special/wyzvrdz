---
name: codebase-search
description: Search files with regex patterns for code, logs, configs, and any text content. Use when the user asks to search code, find patterns, grep files, analyze file contents, or needs to locate specific text across multiple files.
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Codebase Search

This skill provides advanced regex-based search capabilities for text files across the codebase. Use it to find patterns in code, logs, configurations, and any text content.

## When to Use

Use this skill when the user asks for:
- Searching code patterns ("find all functions", "find imports", "grep for X")
- Finding specific text across files ("where is this used", "search for TODO")
- Regex-based searches ("find patterns matching X")
- Code analysis workflows ("find all callers of function Y")
- Log analysis ("find errors in logs", "search for warnings")
- Config file searches ("find all database connections")

## Available Scripts

### `scripts/search_files.py`

Search files by pattern with regex support.

**Usage:**
```bash
python scripts/search_files.py [directory] --pattern "<regex>" [--extensions ".py,.md"] [--content "<search-term>"] [--output json|text]
```

**Examples:**
```bash
# Find all function definitions
python scripts/search_files.py . --pattern "def \w+\(" --extensions ".py"

# Search for TODO comments
python scripts/search_files.py . --content "TODO" --extensions ".py,.md"

# Find all imports
python scripts/search_files.py . --pattern "^import |^from .* import" --extensions ".py"

# Search logs for errors
python scripts/search_files.py logs/ --content "ERROR" --output json
```

**Output:**
- Text mode: File paths with matching lines
- JSON mode: Structured results with file, line number, and match content

### `scripts/search_context.py`

Search with context (show lines before/after matches).

**Usage:**
```bash
python scripts/search_context.py [directory] --pattern "<regex>" [--before N] [--after N] [--extensions ".py"]
```

**Examples:**
```bash
# Find function definitions with 2 lines of context
python scripts/search_context.py . --pattern "def \w+\(" --before 2 --after 2 --extensions ".py"

# Find errors with surrounding context
python scripts/search_context.py logs/ --content "ERROR" --before 3 --after 3
```

### `scripts/count_matches.py`

Count pattern occurrences across files.

**Usage:**
```bash
python scripts/count_matches.py [directory] --pattern "<regex>" [--extensions ".py"]
```

**Examples:**
```bash
# Count TODO comments
python scripts/count_matches.py . --content "TODO" --extensions ".py,.md"

# Count function definitions
python scripts/count_matches.py . --pattern "def \w+\(" --extensions ".py"
```

## Common Workflows

### 1. Find All Function Definitions

```bash
python scripts/search_files.py . --pattern "def \w+\(" --extensions ".py"
```

### 2. Find All Imports

```bash
python scripts/search_files.py . --pattern "^import |^from .* import" --extensions ".py"
```

### 3. Search for TODO/FIXME Comments

```bash
python scripts/search_files.py . --content "TODO|FIXME" --extensions ".py,.md"
```

### 4. Find Class Definitions

```bash
python scripts/search_files.py . --pattern "^class \w+" --extensions ".py"
```

### 5. Search Logs for Errors

```bash
python scripts/search_context.py logs/ --content "ERROR|CRITICAL" --before 2 --after 2
```

### 6. Find All Callers of a Function

```bash
python scripts/search_files.py . --content "my_function\(" --extensions ".py"
```

### 7. Search Config Files for Specific Keys

```bash
python scripts/search_files.py config/ --content "database|db_host|db_user" --extensions ".json,.yaml,.yml"
```

## Code-Specific Patterns

Common regex patterns for code analysis:

| Pattern | Purpose |
|---------|---------|
| `def \w+\(` | Function definitions |
| `^class \w+` | Class definitions |
| `^import |^from .* import` | Import statements |
| `@.*` | Decorators |
| `self\.\w+` | Instance method calls |
| `^\s*def \w+` | Indented functions (methods) |
| `# TODO|# FIXME` | Code comments |
| `raise \w+` | Exception raising |
| `except \w+` | Exception handling |

## Gotchas

- **Regex Escaping**: Special regex characters (`.`, `*`, `?`, etc.) need escaping in patterns. Use `\\.` to match a literal dot.
- **Case Sensitivity**: Searches are case-sensitive by default. Use regex flags for case-insensitive if needed.
- **File Encoding**: UTF-8 is assumed. Files with other encodings may show garbled output.
- **Large Files**: Very large files may take time to search. Consider filtering by directory or extension first.
- **Binary Files**: Binary files are skipped automatically. Only text files are searched.
- **Path Traversal**: Scripts reject paths that escape the base directory for security.
- **Pattern Complexity**: Complex regex patterns may be slow. Test patterns on small directories first.

## References

- `references/code_patterns.md` - Common code search patterns
- `references/regex_examples.md` - Regex pattern examples for various use cases
- `references/log_analysis.md` - Log file search workflows

## See Also

- `filesystem` skill - For basic file operations (read, write, list)
