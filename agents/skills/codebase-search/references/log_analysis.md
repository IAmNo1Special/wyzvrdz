# Log Analysis Workflows

This reference contains workflows for analyzing log files with the codebase-search skill.

## Common Log Patterns

### Error Messages

Find all error-level messages:

```bash
python scripts/search_context.py logs/ --content "ERROR|CRITICAL|FATAL" --before 2 --after 2
```

### Warning Messages

Find all warning-level messages:

```bash
python scripts/search_context.py logs/ --content "WARN|WARNING" --before 1 --after 1
```

### Stack Traces

Find stack trace patterns:

```bash
python scripts/search_context.py logs/ --pattern "Traceback|at .*\(\)|File \".*\", line" --before 0 --after 5
```

### HTTP Error Codes

Find HTTP error codes in access logs:

```bash
python scripts/search_files.py logs/ --pattern " [45]\d{2} " --extensions ".log"
```

## Time-Based Analysis

### Errors in Last Hour

If logs include timestamps, filter by time range:

```bash
# First, extract recent logs
python scripts/search_context.py logs/ --pattern "2026-04-27T0[2-3]:" --content "ERROR" --before 1 --after 1
```

### Errors by Time Period

Count errors by hour:

```bash
python scripts/count_matches.py logs/ --pattern "2026-04-27T\d{2}:" --content "ERROR"
```

## Application-Specific Patterns

### Database Errors

Find database-related errors:

```bash
python scripts/search_context.py logs/ --content "database|db_host|connection|timeout|deadlock" --before 2 --after 2
```

### API Errors

Find API-related errors:

```bash
python scripts/search_context.py logs/ --content "API|endpoint|request failed|status.*[45]\d{2}" --before 2 --after 2
```

### Authentication Failures

Find authentication errors:

```bash
python scripts/search_context.py logs/ --content "auth|login|unauthorized|forbidden|token" --before 1 --after 1
```

## Workflow Examples

### Investigate a Spike in Errors

1. Count total errors:

```bash
python scripts/count_matches.py logs/ --content "ERROR"
```

2. Find error patterns with context:

```bash
python scripts/search_context.py logs/ --content "ERROR" --before 2 --after 2
```

3. Identify common error types:

```bash
python scripts/search_files.py logs/ --pattern "ERROR.*:" --extensions ".log"
```

### Find Specific User Activity

Search for user ID in logs:

```bash
python scripts/search_context.py logs/ --content "user_id:12345" --before 1 --after 1
```

### Debug a Specific Request

Find all log entries for a request ID:

```bash
python scripts/search_context.py logs/ --content "request_id:abc-123" --before 0 --after 0
```

### Monitor Service Health

Check for health check failures:

```bash
python scripts/search_files.py logs/ --content "health.*failed|unhealthy|down" --extensions ".log"
```

## Performance Analysis

### Slow Requests

Find slow request logs (if logged):

```bash
python scripts/search_context.py logs/ --pattern "duration.*[0-9]{4,}" --before 0 --after 0
```

### Memory Issues

Find memory-related errors:

```bash
python scripts/search_context.py logs/ --content "memory|OOM|out of memory|heap" --before 2 --after 2
```

## Gotchas

- **Log Rotation**: Large log directories may have rotated files (app.log, app.log.1, etc.). Search all relevant files.
- **Timestamp Formats**: Different services use different timestamp formats. Adjust patterns accordingly.
- **Log Levels**: Services may use different log level names (ERROR vs err vs error). Search for variations.
- **Structured Logs**: JSON logs require different patterns than plain text logs.
- **Encoding**: Some logs may use non-UTF-8 encoding. Scripts skip files with encoding errors.
