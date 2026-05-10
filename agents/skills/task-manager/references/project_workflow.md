# Project Task Management Workflow

This reference shows a complete workflow for managing project tasks with the task-manager skill.

## Example: Software Development Project

### 1. Create Project List

```bash
python scripts/create_list.py --name "web-app-project" --description "Tasks for building the web application"
```

Output: List ID (e.g., `a1b2c3d4`)

### 2. Add High-Level Tasks

```bash
# Design phase
python scripts/add_task.py --list "a1b2c3d4" --content "Design database schema" --priority high
python scripts/add_task.py --list "a1b2c3d4" --content "Design API endpoints" --priority high

# Implementation phase
python scripts/add_task.py --list "a1b2c3d4" --content "Implement authentication" --priority high
python scripts/add_task.py --list "a1b2c3d4" --content "Implement user CRUD operations" --priority high
python scripts/add_task.py --list "a1b2c3d4" --content "Implement admin panel" --priority medium

# Testing phase
python scripts/add_task.py --list "a1b2c3d4" --content "Write unit tests" --priority medium
python scripts/add_task.py --list "a1b2c3d4" --content "Write integration tests" --priority medium

# Deployment phase
python scripts/add_task.py --list "a1b2c3d4" --content "Set up CI/CD pipeline" --priority low
python scripts/add_task.py --list "a1b2c3d4" --content "Deploy to staging" --priority low
python scripts/add_task.py --list "a1b2c3d4" --content "Deploy to production" --priority low
```

### 3. Track Progress

```bash
# View all tasks
python scripts/list_tasks.py --list "a1b2c3d4"

# Start working on a task
python scripts/update_task.py --task <task-id> --status in_progress

# Complete a task
python scripts/update_task.py --task <task-id> --status completed

# View remaining high-priority tasks
python scripts/list_tasks.py --list "a1b2c3d4" --status pending
```

### 4. Daily Workflow

```bash
# Morning: Check pending high-priority tasks
python scripts/list_tasks.py --list "a1b2c3d4" --status pending

# During work: Update task status as you progress
python scripts/update_task.py --task <task-id> --status in_progress

# End of day: Review completed tasks
python scripts/list_tasks.py --list "a1b2c3d4" --status completed
```

## Example: Research Project

### 1. Create Research List

```bash
python scripts/create_list.py --name "ai-research" --description "Research tasks for AI project"
```

### 2. Add Research Tasks

```bash
python scripts/add_task.py --list <list-id> --content "Survey existing literature" --priority high
python scripts/add_task.py --list <list-id> --content "Identify research gaps" --priority high
python scripts/add_task.py --list <list-id> --content "Design experiments" --priority medium
python scripts/add_task.py --list <list-id> --content "Run experiments" --priority medium
python scripts/add_task.py --list <list-id> --content "Analyze results" --priority medium
python scripts/add_task.py --list <list-id> --content "Write paper" --priority low
```

### 3. Track Research Progress

```bash
# Mark literature survey as complete
python scripts/update_task.py --task <task-id> --status completed

# Start experiments
python scripts/update_task.py --task <task-id> --status in_progress
```

## Best Practices

### Task Breakdown

Break large tasks into smaller, actionable subtasks:

**Too large:**

- "Build the entire application"

**Better:**

- "Design database schema"
- "Implement authentication"
- "Create user interface"
- "Write tests"

### Priority Management

Use priorities to focus on what matters:

- **High**: Critical path items, blockers, must-have features
- **Medium**: Important but not urgent, nice-to-have features
- **Low**: Cleanup, documentation, optimization

### Status Tracking

Use status to track progress:

- **pending**: Not started
- **in_progress**: Currently working on
- **completed**: Done

### Regular Reviews

Review your task list regularly:

- Daily: Check high-priority pending tasks
- Weekly: Review overall progress and reprioritize
- Monthly: Archive completed lists, create new ones for next phase
