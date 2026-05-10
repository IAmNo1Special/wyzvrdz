# Agent Spawn Lifecycle

Complete lifecycle and state transitions for spawned agents.

## State Diagram

```text
[Spawn Request]
     THEN
[Initializing] <- Agent process starting, messageboard created
     THEN
   [Running] <- Agent active, accepting tasks
  ↙    ↘
[Paused]  [Error]
  THEN         THEN
[Stopped] <- Process terminated, cleanup
```

## Lifecycle Stages

### 1. Spawn Request

User requests agent spawn via `spawn_agent.py`.

**Actions:**

- Validate name (must be unique and filesystem-safe)
- Generate UUID
- Create messageboard
- Start subprocess

**Failure Points:**

- Invalid name (contains forbidden characters)
- Duplicate name
- Subprocess spawn failure
- Registry write failure

**On Failure:** Cleanup any partial resources, return error.

### 2. Initializing

Agent process has started but may not be fully ready.

**Duration:** Typically 1-5 seconds

**Actions:**

- Agent loads configuration
- Agent initializes skills
- Agent writes initial heartbeat

**Main Agent Role:**

- Poll `check_agent_health.py` until status = "running"
- Or send test message and wait for acknowledgment

**Failure Points:**

- Agent crashes during startup
- Configuration error
- Resource exhaustion

**On Failure:** Automatically transition to "error" status.

### 3. Running

Agent is active and processing messages.

**Duration:** Until explicitly stopped or timeout reached

**Main Agent Actions:**

- Send tasks via `send_message.py`
- Read results via `read_messages.py`
- Monitor health via `check_agent_health.py`

**Spawned Agent Actions:**

- Poll messageboard for new tasks
- Execute tasks
- Write results to messageboard
- Update heartbeat

**Failure Points:**

- Agent process crash
- Messageboard corruption
- Resource exhaustion

**Auto-Recovery:** None. Requires manual despawn + respawn.

### 4. Paused (Optional)

Agent execution temporarily suspended.

**Trigger:** `send_message.py --type command --content pause`

**Behavior:**

- Agent stops processing new tasks
- Existing tasks complete
- Heartbeat continues

**Resume:** `send_message.py --type command --content resume`

### 5. Error

Agent encountered unrecoverable error.

**Entry Points:**

- Startup failure
- Runtime exception
- Health check timeout

**Behavior:**

- Status updated to "error"
- Error message written to messageboard
- Process may or may not be running

**Recovery:**

1. Check `read_messages.py` for error details
2. `despawn_agent.py` to cleanup
3. `spawn_agent.py` to recreate

### 6. Stopped

Agent has been terminated.

**Entry Points:**

- `despawn_agent.py` called
- Timeout reached (if configured)
- Process self-terminated

**Cleanup Actions:**

- Process terminated (SIGTERM -> SIGKILL if needed)
- Messageboard optionally removed
- Registry entry removed
- Resources freed

## Health Monitoring

### Heartbeat Protocol

Spawned agents should write periodic status updates:

```json
{
  "type": "status",
  "direction": "from_agent",
  "content": "heartbeat",
  "status": "completed"
}
```

**Frequency:** Every 60 seconds (configurable)

**Timeout Detection:**

- If no heartbeat for 180 seconds -> Consider agent dead
- `check_agent_health.py` will show `seconds_since_activity` > 180

### Health Check Script

```bash
python scripts/check_agent_health.py --agent-id <uuid>
```

**Healthy Criteria:**

- `pid_exists`: true
- `status`: "running"
- `seconds_since_activity`: < 180

**Warning Criteria:**

- `seconds_since_activity`: 180-300
- `registry_status` != actual status

**Critical Criteria:**

- `pid_exists`: false (but registry says running)
- `seconds_since_activity`: > 300

## Cleanup Scenarios

### Graceful Despawn

```bash
python scripts/despawn_agent.py --agent-id <uuid>
```

Sequence:

1. Send stop command to agent
2. Wait 5 seconds for graceful shutdown
3. Check if process exited
4. If still running -> SIGTERM
5. Wait 2 seconds
6. If still running -> SIGKILL (if --force)
7. Update messageboard status
8. Remove from registry
9. Optionally remove messageboard file

### Force Despawn (Agent Unresponsive)

```bash
python scripts/despawn_agent.py --agent-id <uuid> --force
```

Sequence:

1. Immediate SIGKILL
2. Update messageboard status
3. Remove from registry
4. Remove messageboard file

### Bulk Despawn

```bash
python scripts/despawn_all_agents.py [--force]
```

Iterates all agents and despawns each.

## Resource Management

### Process Limits

- Maximum spawned agents: Limited by system resources
- Each agent uses: ~100-500MB RAM, 1 CPU core
- Monitor with: `list_spawned_agents.py`

### Messageboard Cleanup

- Messageboards accumulate over time
- Use `despawn_agent.py` to clean up properly
- Or manually remove from `assets/boards/` (not recommended)

### Zombie Detection

Agents where:

- Registry shows status: "running"
- But `pid_exists`: false

These are zombies. Clean with `despawn_agent.py --force`.

## Error Recovery Patterns

### Pattern 1: Respawn on Failure

```bash
# Check health
HEALTH=$(python scripts/check_agent_health.py --agent-id $ID)
STATUS=$(echo $HEALTH | jq -r '.status')

if [ "$STATUS" != "running" ]; then
  # Despawn zombie
  python scripts/despawn_agent.py --agent-id $ID --force

  # Respawn
  NEW=$(python scripts/spawn_agent.py --name "worker" --task "Retry")
  NEW_ID=$(echo $NEW | jq -r '.agent_id')
fi
```

### Pattern 2: Task Retry

```bash
# Read messages
MSGS=$(python scripts/read_messages.py --agent-id $ID --unread-only)

# Check for task failures
echo $MSGS | jq -r '.messages[] | select(.type == "error")' | while read error; do
  # Extract original task
  TASK=$(echo $error | jq -r '.reply_to')
  # Retry with modified parameters
  python scripts/send_message.py --agent-id $ID --type task --content "Retry: $TASK"
done
```

### Pattern 3: Health Check Loop

```bash
while true; do
  python scripts/check_agent_health.py --agent-id $ID
  sleep 60
done
```
