# Process Lifecycle

This reference explains the lifecycle of processes and how to monitor them at different stages.

## Process States

### Running

The process is actively executing on the CPU.

**Check status:**

```bash
python scripts/check_process.py <pid>
```

**Expected output:**

- Status: running
- CPU percentage > 0
- Memory usage stable or increasing

### Sleeping

The process is waiting for an event (I/O, timer, etc.).

**Check status:**

```bash
python scripts/check_process.py <pid>
```

**Expected output:**

- Status: running
- CPU percentage near 0
- Memory usage stable

### Stopped

The process has received a stop signal (SIGSTOP/SIGTSTP).

**Check status:**

```bash
python scripts/check_process.py <pid>
```

**Expected output:**

- Status: running (process still exists)
- CPU percentage 0
- Memory usage frozen

### Zombie

The process has exited but parent hasn't reaped it.

**Check status:**

```bash
python scripts/check_process.py <pid>
```

**Expected output:**

- Status: running (process entry exists)
- CPU percentage 0
- Memory usage 0

### Exited

The process has terminated and been reaped.

**Check status:**

```bash
python scripts/check_process.py <pid>
```

**Expected output:**

- Error: Process not found

## Monitoring Workflow

### 1. Spawn a Process

When spawning a process (via agent-spawner or direct execution):

- Capture the process ID (PID)
- Note the expected process name
- Record the start time

### 2. Monitor During Execution

Periodically check process status:

```bash
python scripts/check_process.py <pid>
```

Watch for:

- CPU spikes (may indicate heavy computation)
- Memory growth (may indicate memory leak)
- Status changes (running → stopped → exited)

### 3. Read Output

If the process is still running:

```bash
python scripts/read_terminal.py <pid>
```

Note: Direct stdout/stderr access requires the process to have been spawned with output capture.

### 4. Handle Exits

When a process exits:

- Check exit code (if available)
- Read any remaining output
- Clean up resources (if needed)

## Common Issues

### Process Not Found

**Cause:** Process has exited or PID is incorrect.

**Solution:**

- Verify the PID is correct
- Check if the process was spawned recently
- List all processes to find the correct PID:

  ```bash
  python scripts/list_processes.py --filter <name>
  ```

### Access Denied

**Cause:** Process belongs to another user or requires elevated permissions.

**Solution:**

- Only monitor processes owned by the current user
- Use appropriate permissions when spawning processes

### Stale PID

**Cause:** PID has been reused by the OS after the original process exited.

**Solution:**

- Verify the process name matches expectations
- Check the process start time
- Use process names in addition to PIDs for identification

## Cross-Platform Notes

### Windows

- Process IDs are integers
- Process names include `.exe` extension
- Use `psutil` for cross-platform compatibility

### Unix/Linux

- Process IDs are integers
- Process names don't include extensions
- Can use `/proc` filesystem for additional information

### macOS

- Similar to Unix/Linux
- Some processes may be protected (system processes)
