# Agent Spawner Examples

Common usage patterns and workflows.

## Example 1: Simple Task Delegation

Spawn an agent to analyze data and return results.

```bash
# Spawn the agent
RESULT=$(python scripts/spawn_agent.py --name "analyzer" --task "Analyze sales data")
AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")

# Wait for initialization
sleep 3

# Check health
python scripts/check_agent_health.py --agent-id $AGENT_ID

# Send specific task
python scripts/send_message.py \
  --agent-id $AGENT_ID \
  --type task \
  --content "Analyze Q4 sales from /data/sales_q4.csv. Calculate total revenue by region."

# Wait for processing
sleep 10

# Read results
python scripts/read_messages.py \
  --agent-id $AGENT_ID \
  --unread-only

# Cleanup
python scripts/despawn_agent.py --agent-id $AGENT_ID
```

## Example 2: Parallel Processing (Map-Reduce)

Spawn multiple agents to process chunks in parallel.

```bash
#!/bin/bash

# Split work into chunks
CHUNKS=("chunk1.csv" "chunk2.csv" "chunk3.csv" "chunk4.csv")
AGENT_IDS=()

# Spawn agents
for chunk in "${CHUNKS[@]}"; do
  RESULT=$(python scripts/spawn_agent.py \
    --name "worker-$chunk" \
    --task "Process $chunk")

  AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
  AGENT_IDS+=("$AGENT_ID")

  # Send processing task
  python scripts/send_message.py \
    --agent-id $AGENT_ID \
    --type task \
    --content "Process /data/$chunk and extract key metrics"
done

# Monitor progress
echo "Processing with ${#AGENT_IDS[@]} agents..."
for i in {1..30}; do
  sleep 5

  COMPLETED=0
  for AGENT_ID in "${AGENT_IDS[@]}"; do
    MESSAGES=$(python scripts/read_messages.py --agent-id $AGENT_ID --unread-only)
    RESULTS=$(echo $MESSAGES | grep -c '"type": "result"' || true)
    if [ "$RESULTS" -gt 0 ]; then
      COMPLETED=$((COMPLETED + 1))
    fi
  done

  echo "Progress: $COMPLETED/${#AGENT_IDS[@]} agents completed"

  if [ "$COMPLETED" -eq "${#AGENT_IDS[@]}" ]; then
    break
  fi
done

# Collect all results
ALL_RESULTS=()
for AGENT_ID in "${AGENT_IDS[@]}"; do
  MESSAGES=$(python scripts/read_messages.py --agent-id $AGENT_ID --direction from_agent)
  ALL_RESULTS+=("$MESSAGES")
done

# Despawn all
python scripts/despawn_all_agents.py
```

## Example 3: Long-Running Background Agent

Spawn an agent that runs continuously, processing tasks as they arrive.

```bash
# Spawn persistent agent
RESULT=$(python scripts/spawn_agent.py \
  --name "background-worker" \
  --task "Background processing service")

AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")

# Function to submit work
submit_task() {
  local task_content="$1"
  python scripts/send_message.py \
    --agent-id $AGENT_ID \
    --type task \
    --content "$task_content"
}

# Submit multiple tasks over time
submit_task "Process item A"
submit_task "Process item B"
submit_task "Process item C"

# Check results periodically
while true; do
  python scripts/read_messages.py --agent-id $AGENT_ID --unread-only
  sleep 30
done

# When done, despawn
python scripts/despawn_agent.py --agent-id $AGENT_ID
```

## Example 4: Health Monitoring & Auto-Recovery

Monitor agent health and respawn if needed.

```bash
#!/bin/bash

AGENT_NAME="critical-worker"
AGENT_ID=""

start_agent() {
  RESULT=$(python scripts/spawn_agent.py \
    --name "$AGENT_NAME" \
    --task "Critical processing task")

  AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
  echo "Started agent: $AGENT_ID"
}

check_and_recover() {
  if [ -z "$AGENT_ID" ]; then
    echo "No agent ID, starting fresh..."
    start_agent
    return
  fi

  HEALTH=$(python scripts/check_agent_health.py --agent-id $AGENT_ID)
  STATUS=$(echo $HEALTH | python -c "import sys,json; print(json.load(sys.stdin).get('status', 'unknown'))")

  if [ "$STATUS" != "running" ]; then
    echo "Agent $AGENT_ID not running (status: $STATUS), restarting..."

    # Cleanup old agent
    python scripts/despawn_agent.py --agent-id $AGENT_ID --force 2>/dev/null || true

    # Start new agent
    start_agent
  else
    echo "Agent $AGENT_ID healthy"
  fi
}

# Initial start
start_agent

# Monitor loop
while true; do
  check_and_recover
  sleep 60
done
```

## Example 5: Result Aggregation

Spawn multiple research agents and aggregate results.

```bash
#!/bin/bash

TOPICS=("Quantum Computing" "AI Ethics" "Climate Tech")
AGENT_IDS=()

# Spawn research agents
for topic in "${TOPICS[@]}"; do
  SAFE_NAME=$(echo "$topic" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

  RESULT=$(python scripts/spawn_agent.py \
    --name "research-$SAFE_NAME" \
    --task "Research $topic")

  AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")
  AGENT_IDS+=("$AGENT_ID")

  python scripts/send_message.py \
    --agent-id $AGENT_ID \
    --type task \
    --content "Research $topic. Provide summary of: 1) Key developments 2) Major players 3) Future outlook"
done

# Wait for completion
sleep 30

# Aggregate results
REPORTS_DIR="/tmp/research-reports"
mkdir -p $REPORTS_DIR

for i in "${!AGENT_IDS[@]}"; do
  AGENT_ID="${AGENT_IDS[$i]}"
  TOPIC="${TOPICS[$i]}"

  MESSAGES=$(python scripts/read_messages.py --agent-id $AGENT_ID --direction from_agent)
  echo $MESSAGES > "$REPORTS_DIR/$TOPIC.json"
done

# Generate summary report
echo "=== Research Summary ==="
for file in $REPORTS_DIR/*.json; do
  echo ""
  echo "Topic: $(basename "$file" .json)"
  echo "---"
  cat "$file" | python -c "import sys,json; data=json.load(sys.stdin); print(data)"
done

# Cleanup
python scripts/despawn_all_agents.py
```

## Example 6: Interactive Agent Communication

Two-way conversation with a spawned agent.

```bash
#!/bin/bash

# Spawn agent
RESULT=$(python scripts/spawn_agent.py \
  --name "collaborator" \
  --task "Collaborative problem solving")

AGENT_ID=$(echo $RESULT | python -c "import sys,json; print(json.load(sys.stdin)['agent_id'])")

# Interactive loop
while true; do
  echo ""
  echo "Enter message (or 'quit' to exit):"
  read -r message

  if [ "$message" = "quit" ]; then
    break
  fi

  # Send message
  python scripts/send_message.py \
    --agent-id $AGENT_ID \
    --type task \
    --content "$message"

  # Wait for response
  sleep 5

  # Read response
  echo ""
  echo "Agent response:"
  python scripts/read_messages.py \
    --agent-id $AGENT_ID \
    --unread-only

  echo ""
  echo "---"
done

# Cleanup
python scripts/despawn_agent.py --agent-id $AGENT_ID
```

## Example 7: Scheduled Agent Spawn

Spawn agents at scheduled times (requires cron-manager skill).

```bash
# Register recurring task in cron-manager
# This will spawn a data processing agent every hour

# The cron job would execute:
python scripts/spawn_agent.py \
  --name "hourly-processor-$(date +%H)" \
  --task "Hourly data processing" \
  --timeout 3300  # 55 minutes, must complete before next run

# After processing, agent should self-terminate or be despawned by cron-manager
```

## Best Practices

### Naming Conventions

- Use lowercase with hyphens: `research-agent-1`
- Include timestamp for unique names: `worker-$(date +%s)`
- Keep names under 64 characters

### Resource Management

- Spawn only what you need
- Always cleanup with `despawn_agent.py`
- Monitor with `list_spawned_agents.py`
- Set timeouts for long-running tasks

### Error Handling

- Check health before sending critical tasks
- Handle "zombie" agents (pid not found but registry shows running)
- Retry failed spawns with exponential backoff
- Log all spawn/despawn operations

### Security Considerations

- Spawned agents have same permissions as parent
- Messageboards are plain JSON files
- Don't put sensitive data in agent names or tasks
- Clean up messageboards when done
