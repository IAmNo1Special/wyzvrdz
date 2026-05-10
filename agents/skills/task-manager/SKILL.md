---
name: task-manager
description: Create, update, and manage todo lists for tracking tasks and projects. Use when the user asks to create a todo list, add tasks, track progress, manage project tasks, or mentions "todo", "task list", "checklist", or "reminders".
metadata:
  version: 0.1.0
  author: IAmNo1Special
---

# Task Manager

This skill provides todo list management capabilities for tracking tasks and projects. Use it to create task lists, add/update tasks, and track progress.

## When to Use

Use this skill when the user asks for:
- Creating a todo list ("make a todo list", "create a checklist")
- Adding tasks ("add this to my tasks", "track this")
- Updating task status ("mark this as done", "complete this task")
- Viewing tasks ("show my tasks", "what's on my list")
- Managing project tasks ("track project progress", "task list for X")
- Organizing work ("organize my tasks", "prioritize tasks")

## Available Scripts

### `scripts/create_list.py`

Create a new todo list.

**Usage:**
```bash
python scripts/create_list.py --name <list-name> [--description <description>]
```

**Examples:**
```bash
# Create a new list
python scripts/create_list.py --name "project-tasks" --description "Tasks for the AI project"

# Create a simple list
python scripts/create_list.py --name "my-todos"
```

**Output:**
- List ID
- List name
- Creation timestamp

### `scripts/add_task.py`

Add a task to a list.

**Usage:**
```bash
python scripts/add_task.py --list <list-id> --content <task-content> [--priority low|medium|high]
```

**Examples:**
```bash
# Add a high-priority task
python scripts/add_task.py --list "project-tasks" --content "Implement authentication" --priority high

# Add a low-priority task
python scripts/add_task.py --list "my-todos" --content "Buy groceries" --priority low
```

**Output:**
- Task ID
- Task content
- Priority
- Status (pending)

### `scripts/update_task.py`

Update a task's status or content.

**Usage:**
```bash
python scripts/update_task.py --task <task-id> [--status pending|in_progress|completed] [--content <new-content>] [--priority low|medium|high]
```

**Examples:**
```bash
# Mark task as completed
python scripts/update_task.py --task "task-123" --status completed

# Update task content
python scripts/update_task.py --task "task-123" --content "Implement OAuth2 authentication"

# Change priority
python scripts/update_task.py --task "task-123" --priority high
```

**Output:**
- Updated task information

### `scripts/list_tasks.py`

List all tasks in a list.

**Usage:**
```bash
python scripts/list_tasks.py --list <list-id> [--status pending|in_progress|completed|all]
```

**Examples:**
```bash
# List all tasks
python scripts/list_tasks.py --list "project-tasks"

# List only pending tasks
python scripts/list_tasks.py --list "project-tasks" --status pending

# List completed tasks
python scripts/list_tasks.py --list "project-tasks" --status completed
```

**Output:**
- List of tasks with ID, content, priority, and status

### `scripts/delete_task.py`

Delete a task from a list.

**Usage:**
```bash
python scripts/delete_task.py --task <task-id>
```

**Examples:**
```bash
# Delete a task
python scripts/delete_task.py --task "task-123"
```

**Output:**
- Confirmation of deletion

### `scripts/list_lists.py`

List all todo lists.

**Usage:**
```bash
python scripts/list_lists.py
```

**Output:**
- List of all todo lists with IDs and names

## Common Workflows

### 1. Create a Project Task List

```bash
# Create the list
python scripts/create_list.py --name "project-tasks" --description "AI project tasks"

# Add tasks
python scripts/add_task.py --list "project-tasks" --content "Design database schema" --priority high
python scripts/add_task.py --list "project-tasks" --content "Implement API endpoints" --priority high
python scripts/add_task.py --list "project-tasks" --content "Write tests" --priority medium
```

### 2. Track Progress

```bash
# Start a task
python scripts/update_task.py --task "task-123" --status in_progress

# Complete a task
python scripts/update_task.py --task "task-123" --status completed

# View remaining tasks
python scripts/list_tasks.py --list "project-tasks" --status pending
```

### 3. Prioritize Work

```bash
# View high-priority tasks
python scripts/list_tasks.py --list "project-tasks" --status pending

# Reorder by changing priorities
python scripts/update_task.py --task "task-456" --priority high
```

## Data Storage

Todo lists are stored as JSON files in the `assets/` directory:

```
assets/
└── todo_lists/
    ├── <list-id>.json
    └── ...
```

Each list file contains:
- List metadata (name, description, created_at)
- Tasks array (id, content, priority, status, created_at, updated_at)

## Gotchas

- **List ID vs Name**: Use the list ID (not name) when adding tasks. The ID is returned when creating a list.
- **Task ID**: Each task has a unique ID. Use this ID when updating or deleting tasks.
- **Priority Levels**: Only three priority levels are supported: low, medium, high.
- **Status Values**: Valid status values are: pending, in_progress, completed.
- **File Persistence**: Lists are stored as JSON files. Ensure the `assets/` directory exists and is writable.
- **Concurrent Access**: Multiple processes may conflict when writing to the same list file. Use file locking for critical operations.

## References

- `references/project_workflow.md` - Example project task management workflow
- `references/task_templates.md` - Common task templates for different use cases

## See Also

- `cron-manager` skill - For scheduling recurring tasks
- `filesystem` skill - For managing task list files directly if needed
