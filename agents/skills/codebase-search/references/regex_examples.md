# Regex Examples

This reference provides regex pattern examples for various search scenarios.

## Basic Patterns

### Literal String Match
```regex
hello
```
Matches the literal string "hello" (case-sensitive).

### Case-Insensitive Match
```regex
(?i)hello
```
Matches "hello", "Hello", "HELLO", etc. (using inline flag).

### Word Boundary
```regex
\btest\b
```
Matches "test" as a whole word, not "testing" or "contest".

### Alternation (OR)
```regex
error|warning|info
```
Matches "error" OR "warning" OR "info".

### Character Class
```regex
[abc]
```
Matches any single character: 'a', 'b', or 'c'.

### Negated Character Class
```regex
[^abc]
```
Matches any character except 'a', 'b', or 'c'.

### Range
```regex
[a-z]
```
Matches any lowercase letter.

### Digit
```regex
\d
```
Matches any digit (0-9).

### Non-Digit
```regex
\D
```
Matches any non-digit character.

### Whitespace
```regex
\s
```
Matches any whitespace character (space, tab, newline).

### Non-Whitespace
```regex
\S
```
Matches any non-whitespace character.

## Quantifiers

### Zero or More
```regex
a*
```
Matches zero or more 'a' characters.

### One or More
```regex
a+
```
Matches one or more 'a' characters.

### Zero or One
```regex
a?
```
Matches zero or one 'a' character.

### Exact Count
```regex
a{3}
```
Matches exactly 3 'a' characters.

### Range
```regex
a{2,4}
```
Matches 2 to 4 'a' characters.

### Minimum
```regex
a{2,}
```
Matches 2 or more 'a' characters.

## Anchors

### Start of Line
```regex
^import
```
Matches "import" only at the start of a line.

### End of Line
```regex
:$
```
Matches colon at the end of a line.

## Groups and Capturing

### Capturing Group
```regex
(\w+)\s*=\s*(\w+)
```
Captures key and value in "key = value".

### Non-Capturing Group
```regex
(?:error|warning)
```
Groups without capturing.

## Escaping Special Characters

Special regex characters that need escaping with backslash:
- `. * + ? ^ $ { } [ ] \ | ( )`

Example:
```regex
file\.txt
```
Matches "file.txt" (literal dot, not any character).

## Practical Examples

### Match Function Call with Arguments
```regex
\w+\([^)]*\)
```
Matches function calls like `func()` or `func(arg1, arg2)`.

### Match IP Address
```regex
\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}
```
Matches IPv4 addresses (basic pattern).

### Match Email
```regex
[\w.+-]+@[\w-]+\.[\w.-]+
```
Matches email addresses.

### Match UUID
```regex
[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
```
Matches UUID format.

### Match Hex Color Code
```regex
#[0-9a-fA-F]{6}
```
Matches 6-digit hex color codes like "#FF0000".

### Match JSON Key
```regex
"\w+"\s*:
```
Matches JSON keys like `"name":`.

### Match Python List
```regex
\[.*?\]
```
Matches square brackets with content (non-greedy).

### Match Python Dictionary
```regex
\{.*?\}
```
Matches curly braces with content (non-greedy).

## Common Gotchas

### Greedy vs Non-Greedy
```regex
# Greedy (matches as much as possible)
<div>.*</div>

# Non-greedy (matches as little as possible)
<div>.*?</div>
```

### Dot Doesn't Match Newlines
By default, `.` doesn't match newline characters. Use `[\s\S]` to match any character including newlines.

### Escaping in Shell
When using regex in shell commands, you may need to escape backslashes:
```bash
# In Python script
--pattern "def \w+\("

# In shell (may need double escaping)
--pattern "def \\w+\\("
```

## Testing Patterns

Always test regex patterns on a small sample before running on large directories:
```bash
# Test on single file first
python scripts/search_files.py test_file.py --pattern "your_pattern"

# Then run on directory
python scripts/search_files.py . --pattern "your_pattern" --extensions ".py"
```
