---
name: agent-spawner
description: Spawn independent agent instances that run in separate processes and communicate via JSON messageboards. Use when you need to run multiple agents in parallel, delegate tasks to background agents, or create agent swarms for distributed processing. Each spawned agent gets its own isolated messageboard for bidirectional communication with the main agent.
metadata:
  version: 0.1.0
  author: IAmNo1Special
  adk_additional_tools:
    - WyzvrdFactory
---

# Agent Spawner

This skill enables spawning independent Wyzvrd agent instances as separate processes. Spawned agents communicate with the main agent via JSON messageboards.

## When to Use

Use this skill when:
- You need to run multiple agents in parallel for concurrent task processing
- You want to delegate long-running tasks to background agents
- You need to create agent swarms for distributed processing
- You want fault isolation (spawned agents crash independently)
- You need to scale processing across multiple agent instances

## Architecture Overview

```
Main Agent (Parent Process)
    ├── Spawned Agent #1 <--> Messageboard #1 (JSON file)
    ├── Spawned Agent #2 <--> Messageboard #2 (JSON file)
    └── Spawned Agent #N <--> Messageboard #N (JSON file)
```

**Key Concepts:**
- **Spawned Agent**: Independent process running a full Wyzvrd instance
- **Messageboard**: JSON file used for bidirectional communication
- **Registry**: JSON file tracking all spawned agents (PID, messageboard path, status)

## Messageboard Protocol

Each messageboard is a JSON file with the following structure:

```json
{
  "agent_id": "uuid-of-spawned-agent",
  "created_at": "2026-01-01T12:00:00Z",
  "last_activity": "2026-01-01T12:05:00Z",
  "status": "running",
  "messages": [
    {
      "id": "msg-001",
      "timestamp": "2026-01-01T12:01:00Z",
      "direction": "to_agent",
      "type": "task",
      "content": "Analyze this data...",
      "status": "pending"
    },
    {
      "id": "msg-002",
      "timestamp": "2026-01-01T12:02:00Z",
      "direction": "from_agent",
      "type": "result",
      "content": "Analysis complete...",
      "status": "completed",
      "reply_to": "msg-001"
    }
  ]
}
```

**Message Types:**
- `task`: Assignment from main agent to spawned agent
- `result`: Output from spawned agent back to main agent
- `status`: Health check or progress update
- `command`: Control directive (pause, resume, stop)

## Available Scripts

### `scripts/spawn_agent.py`

Spawn a new independent agent instance.

**Usage:**
```bash
python scripts/spawn_agent.py --name "research-agent-1" --task "Research quantum computing" [--timeout 300]
```

**Output:**
```json
{
  "success": true,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "research-agent-1",
  "pid": 12345,
  "messageboard_path": "agents/skills/agent-spawner/assets/boards/research-agent-1.json",
  "status": "running",
  "created_at": "2026-01-01T12:00:00Z"
}
```

### `scripts/send_message.py`

Send a message to a spawned agent via its messageboard.

**Usage:**
```bash
python scripts/send_message.py --agent-id <uuid> --type task --content "New task description"
```

**Output:**
```json
{
  "success": true,
  "message_id": "msg-003",
  "timestamp": "2026-01-01T12:03:00Z"
}
```

### `scripts/read_messages.py`

Read messages from a spawned agent's messageboard.

**Usage:**
```bash
python scripts/read_messages.py --agent-id <uuid> [--since "2026-01-01T12:00:00Z"] [--unread-only]
```

**Output:**
```json
{
  "success": true,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": "msg-002",
      "timestamp": "2026-01-01T12:02:00Z",
      "direction": "from_agent",
      "type": "result",
      "content": "Analysis complete...",
      "status": "completed"
    }
  ]
}
```

### `scripts/list_spawned_agents.py`

List all spawned agents from the registry.

**Usage:**
```bash
python scripts/list_spawned_agents.py [--status running|stopped|all]
```

**Output:**
```json
{
  "success": true,
  "count": 3,
  "agents": [
    {
      "agent_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "research-agent-1",
      "pid": 12345,
      "status": "running",
      "messageboard_path": "...",
      "created_at": "2026-01-01T12:00:00Z",
      "last_activity": "2026-01-01T12:05:00Z"
    }
  ]
}
```

### `scripts/despawn_agent.py`

Stop and cleanup a spawned agent.

**Usage:**
```bash
python scripts/despawn_agent.py --agent-id <uuid> [--force]
```

**Output:**
```json
{
  "success": true,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "pid": 12345,
  "terminated": true,
  "messageboard_cleaned": true
}
```

### `scripts/despawn_all_agents.py`

Stop all spawned agents.

**Usage:**
```bash
python scripts/despawn_all_agents.py [--force]
```

**Output:**
```json
{
  "success": true,
  "terminated_count": 3,
  "failed_count": 0,
  "terminated_agents": ["uuid-1", "uuid-2", "uuid-3"]
}
```

### `scripts/check_agent_health.py`

Check if a spawned agent is still running.

**Usage:**
```bash
python scripts/check_agent_health.py --agent-id <uuid>
```

**Output:**
```json
{
  "success": true,
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "pid": 12345,
  "pid_exists": true,
  "last_heartbeat": "2026-01-01T12:05:00Z",
  "seconds_since_activity": 45
}
```

## Common Workflows

### 1. Spawn and Assign Task

```bash
# Spawn a new agent
RESULT=$(python scripts/spawn_agent.py --name "analyzer-1" --task "Analyze sales data")
AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")

# Send a specific task
python scripts/send_message.py --agent-id $AGENT_ID --type task --content "Analyze Q4 sales data from /data/sales.csv"
```

### 2. Check Progress and Get Results

```bash
# Check health
python scripts/check_agent_health.py --agent-id $AGENT_ID

# Read results
python scripts/read_messages.py --agent-id $AGENT_ID --unread-only
```

### 3. Cleanup

```bash
# Despawn specific agent
python scripts/despawn_agent.py --agent-id $AGENT_ID

# Or despawn all
python scripts/despawn_all_agents.py
```

### 4. Parallel Processing Pattern

```bash
# Spawn multiple agents for parallel work
for i in {1..5}; do
  python scripts/spawn_agent.py --name "worker-$i" --task "Process chunk $i"
done

# Monitor all
python scripts/list_spawned_agents.py --status running

# Cleanup when done
python scripts/despawn_all_agents.py
```

## File Structure

Assets are stored in the `filesystem` skill for centralized management:

```
filesystem/assets/
├── registry.json              # Master registry of all spawned agents
└── boards/                    # Messageboard directory
    ├── agent-1.json
    ├── agent-2.json
    └── ...
```

The agent-spawner scripts use `filesystem/assets/` as the base directory for all agent data storage.

## Gotchas

- **Process Isolation**: Spawned agents run as separate processes. They don't share memory with the main agent.
- **Messageboard Persistence**: Messageboards are JSON files on disk. Clean up with `despawn_agent.py` to remove.
- **PID Reuse**: After despawn, the PID might be reused by the OS. Always check agent_id, not just PID.
- **Resource Limits**: Each spawned agent uses memory and CPU. Monitor system resources when spawning many agents.
- **Zombie Processes**: If an agent crashes, use `--force` with despawn to clean up the registry entry.
- **Messageboard Concurrency**: Multiple processes may read/write messageboards. The scripts handle file locking, but avoid manual edits.

## References

- `references/messageboard_schema.md` - Complete messageboard JSON schema
- `references/spawn_lifecycle.md` - Agent lifecycle and state transitions
- `references/examples.md` - Common usage examples

## See Also

- `filesystem` skill - For managing messageboard files directly
- `cron-manager` skill - For scheduling periodic agent spawns
