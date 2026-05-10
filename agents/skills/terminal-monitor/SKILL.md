---
name: terminal-monitor
description: Monitor and read terminal process output for running commands and background tasks. Use when the user asks to check process status, read terminal output, monitor background jobs, or needs to see what a process is printing to stdout/stderr.
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Terminal Monitor

This skill provides capabilities to monitor and read output from terminal processes. Use it to check the status of running commands, monitor background tasks, and read stdout/stderr from processes.

## When to Use

Use this skill when the user asks for:

- Checking process status ("is the process still running?")
- Reading terminal output ("show me what the process printed")
- Monitoring background jobs ("check on the background task")
- Viewing command output ("what did the command output?")
- Debugging process issues ("why is the process failing?")

## Available Scripts

### `scripts/read_terminal.py`

Read output from a terminal process by process ID.

**Usage:**

```bash
python scripts/read_terminal.py <process_id> [--name <name>]
```

**Examples:**

```bash
# Read output from process with PID 12345
python scripts/read_terminal.py 12345

# Read output with a friendly name
python scripts/read_terminal.py 12345 --name "my-background-job"
```

**Output:**

- stdout content from the process
- stderr content from the process
- Process status information

### `scripts/check_process.py`

Check if a process is still running.

**Usage:**

```bash
python scripts/check_process.py <process_id>
```

**Examples:**

```bash
# Check if process 12345 is running
python scripts/check_process.py 12345
```

**Output:**

- Process status (running/stopped)
- Process name (if available)
- CPU/memory usage (if available)

### `scripts/list_processes.py`

List all processes that can be monitored.

**Usage:**

```bash
python scripts/list_processes.py [--filter <pattern>]
```

**Examples:**

```bash
# List all monitorable processes
python scripts/list_processes.py

# Filter by name pattern
python scripts/list_processes.py --filter "python"
```

**Output:**

- List of process IDs
- Process names
- Start times

## Common Workflows

### 1. Monitor a Background Task

```bash
# Check if the process is still running
python scripts/check_process.py 12345

# Read the output
python scripts/read_terminal.py 12345
```

### 2. Debug a Failing Process

```bash
# Check process status
python scripts/check_process.py 12345

# Read stderr for error messages
python scripts/read_terminal.py 12345
```

### 3. Monitor Multiple Processes

```bash
# List all running processes
python scripts/list_processes.py

# Read output from specific processes
python scripts/read_terminal.py 12345
python scripts/read_terminal.py 12346
```

## Integration with Agent Spawner

When using the `agent-spawner` skill to spawn background agents, use `terminal-monitor` to check their output:

1. Spawn an agent (via `agent-spawner`)
1. Get the process ID from the spawn result
1. Monitor the agent's output:
   ```bash
   python scripts/read_terminal.py <agent_pid>
   ```

## Gotchas

- **Process Permissions**: Can only monitor processes owned by the current user. System processes may not be accessible.
- **Process ID Reuse**: Process IDs can be reused after a process exits. Always verify the process is the expected one.
- **Output Buffering**: Some processes buffer output. Output may not appear immediately.
- **Terminal Emulation**: This skill reads raw output, not terminal emulation. ANSI escape codes may appear in the output.
- **Process Lifetime**: Once a process exits, its output may no longer be available. Read output before the process terminates if needed.
- **Cross-Platform**: Process monitoring works differently on Windows vs Unix. Scripts handle platform differences automatically.

## References

- `references/process_lifecycle.md` - Process lifecycle and state transitions
- `references/integration_examples.md` - Examples with agent-spawner skill

## See Also

- `agent-spawner` skill - For spawning background agents that can be monitored
