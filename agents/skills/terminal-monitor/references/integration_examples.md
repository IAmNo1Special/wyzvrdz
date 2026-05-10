# Integration Examples

This reference shows how to use terminal-monitor with other skills.

## Agent Spawner Integration

When using the `agent-spawner` skill to spawn background agents, use `terminal-monitor` to check their status and output.

### Workflow

1. Spawn an agent via agent-spawner:

   ```bash
   python agents/skills/agent-spawner/scripts/spawn_agent.py --name "research-agent" --task "Analyze data"
   ```

2. Get the process ID from the spawn result (PID field in JSON output)

3. Monitor the agent:

   ```bash
   # Check if it's still running
   python agents/skills/terminal-monitor/scripts/check_process.py <pid>

   # Read process information
   python agents/skills/terminal-monitor/scripts/read_terminal.py <pid>
   ```

### Example

```bash
# Spawn agent
SPAWN_RESULT=$(python agents/skills/agent-spawner/scripts/spawn_agent.py --name "worker-1" --task "Process data")
PID=$(echo $SPAWN_RESULT | python -c "import sys,json; print(json.load(sys.stdin)['pid'])")

# Monitor
python agents/skills/terminal-monitor/scripts/check_process.py $PID
```

## Cron Manager Integration

When using the `cron-manager` skill for scheduled tasks, use `terminal-monitor` to check if the cron service is running.

### Cron Workflow

1. Check cron service status:

   ```bash
   python agents/skills/terminal-monitor/scripts/list_processes.py --filter "cron"
   ```

2. Monitor the cron service process if found

## General Background Tasks

For any background task started by the agent:

1. Capture the process ID when starting the task
2. Store the PID in a registry file (via filesystem skill)
3. Use terminal-monitor to check status periodically
4. Read output when needed

### Example Registry Entry

```json
{
  "task_name": "data-processing",
  "pid": 12345,
  "started_at": "2026-04-27T12:00:00Z",
  "status": "running"
}
```

### Monitoring Script

```bash
# Read registry
TASK_INFO=$(python agents/skills/filesystem/scripts/read_file.py tasks/registry.json)

# Extract PID
PID=$(echo $TASK_INFO | python -c "import sys,json; print(json.load(sys.stdin)['pid'])")

# Check status
python agents/skills/terminal-monitor/scripts/check_process.py $PID
```
