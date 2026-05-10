# Messageboard JSON Schema

Complete schema specification for agent messageboards.

## Top-Level Structure

```json
{
  "agent_id": "string (UUID)",
  "agent_name": "string",
  "created_at": "ISO 8601 timestamp",
  "last_activity": "ISO 8601 timestamp",
  "status": "running | stopped | error",
  "pid": "integer (process ID)",
  "messages": [Message]
}
```

## Message Object

```json
{
  "id": "string (unique message ID)",
  "timestamp": "ISO 8601 timestamp",
  "direction": "to_agent | from_agent",
  "type": "task | result | status | command | error",
  "content": "string (message content)",
  "status": "pending | completed | failed | read",
  "reply_to": "string (optional, references another message id)",
  "metadata": "object (optional, additional data)"
}
```

## Field Descriptions

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | UUID | Unique identifier for the agent |
| `agent_name` | string | Human-readable name |
| `created_at` | ISO timestamp | When messageboard was created |
| `last_activity` | ISO timestamp | Last read or write |
| `status` | enum | Current agent status |
| `pid` | integer | OS process ID |
| `messages` | array | List of messages |

### Message Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message identifier (msg-*) |
| `timestamp` | ISO timestamp | When message was sent |
| `direction` | enum | Message flow direction |
| `type` | enum | Message category |
| `content` | string | Message body |
| `status` | enum | Processing status |
| `reply_to` | string | Optional parent message ID |
| `metadata` | object | Optional structured data |

## Message Types

### task
Assignment from main agent to spawned agent.

```json
{
  "type": "task",
  "direction": "to_agent",
  "content": "Analyze Q4 sales data",
  "status": "pending"
}
```

### result
Output from spawned agent back to main agent.

```json
{
  "type": "result",
  "direction": "from_agent",
  "content": "Analysis complete. Revenue increased 15%...",
  "status": "completed",
  "reply_to": "msg-001",
  "metadata": {
    "files_generated": ["report.pdf"]
  }
}
```

### status
Health check or progress update.

```json
{
  "type": "status",
  "direction": "from_agent",
  "content": "Processing: 50% complete",
  "status": "pending"
}
```

### command
Control directive from main agent.

```json
{
  "type": "command",
  "direction": "to_agent",
  "content": "pause",
  "status": "completed"
}
```

### error
Error notification from spawned agent.

```json
{
  "type": "error",
  "direction": "from_agent",
  "content": "Failed to read file: permission denied",
  "status": "failed"
}
```

## Status Values

### Message Status
- `pending` - Message sent but not yet processed
- `completed` - Message processed successfully
- `failed` - Processing failed
- `read` - Message has been read (for from_agent messages)

### Agent Status
- `initializing` - Agent starting up
- `running` - Agent active and processing
- `stopped` - Agent terminated
- `error` - Agent encountered error

## Concurrency & Locking

Messageboards use file-level locking:
- Reads acquire shared lock (multiple readers ok)
- Writes acquire exclusive lock (single writer)

Always use the provided scripts (`send_message.py`, `read_messages.py`) rather than direct file manipulation to ensure proper locking.
