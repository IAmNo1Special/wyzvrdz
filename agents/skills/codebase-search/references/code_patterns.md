# Common Code Search Patterns

This reference contains common regex patterns for code analysis workflows.

## Python Patterns

### Function Definitions

```regex
def \w+\(
```

Finds all function definitions including `def my_function(`.

### Class Definitions

```regex
^class \w+
```

Finds all class definitions at the start of a line.

### Import Statements

```regex
^import |^from .* import
```

Finds all import statements (both `import X` and `from X import Y`).

### Decorators

```regex
@\w+
```

Finds all decorators (e.g., `@property`, `@staticmethod`).

### Method Calls

```regex
self\.\w+\(
```

Finds instance method calls.

### Exception Raising

```regex
raise \w+
```

Finds exception raising statements.

### Exception Handling

```regex
except \w+
```

Finds exception handling blocks.

### Docstrings

```regex
""".*?"""
```

Finds multi-line docstrings (use with DOTALL flag).

## JavaScript/TypeScript Patterns

### JS/TS Function Definitions

```regex
function \w+\(|const \w+ = \(|\w+:\s*\(.*\)\s*=>\s*{
```

Finds function definitions in various JS syntaxes.

### JS/TS Class Definitions

```regex
class \w+
```

Finds class definitions.

### Import/Export

```regex
^import |^export |require\(
```

Finds import and export statements.

## General Patterns

### Comments

```regex
# .*|// .*|/\*.*?\*/
```

Finds single-line and multi-line comments (Python, JS, C-style).

### TODO/FIXME

```regex
# TODO|# FIXME|// TODO|// FIXME
```

Finds TODO and FIXME comments.

### String Literals

```regex
['"`].*?['"`]
```

Finds string literals (single or double quoted).

### Numbers

```regex
\b\d+\b
```

Finds integer numbers.

### URLs

```regex
https?://[^\s]+
```

Finds HTTP/HTTPS URLs.

### Email Addresses

```regex
[\w.+-]+@[\w-]+\.[\w.-]+
```

Finds email addresses.

## Log Patterns

### Error Messages

```regex
ERROR|CRITICAL|FATAL
```

Finds error-level log messages.

### Warning Messages

```regex
WARN|WARNING
```

Finds warning-level log messages.

### Timestamps (ISO 8601)

```regex
\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
```

Finds ISO 8601 timestamps.

### Timestamps (Common Log Format)

```regex
\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}
```

Finds common log format timestamps.

## Config Patterns

### Database Connections

```regex
database|db_host|db_user|db_pass|connection_string
```

Finds database-related configuration keys.

### API Keys

```regex
api_key|apikey|api-key|secret_key|secret
```

Finds API key configuration keys.

### File Paths

```regex
/[^\s]+|\\[^\s]+
```

Finds Unix or Windows file paths.

## Usage Examples

### Find all function definitions in Python files

```bash
python scripts/search_files.py . --pattern "def \w+\(" --extensions ".py"
```

### Find all TODO comments

```bash
python scripts/search_files.py . --content "TODO|FIXME" --extensions ".py,.md"
```

### Find all database connections in config files

```bash
python scripts/search_files.py config/ --content "database|db_host" --extensions ".json,.yaml"
```

### Find errors in logs with context

```bash
python scripts/search_context.py logs/ --content "ERROR" --before 2 --after 2
```

### Count all import statements

```bash
python scripts/count_matches.py . --pattern "^import |^from .* import" --extensions ".py"
```
