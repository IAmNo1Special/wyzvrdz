# Example: Multi-Step File Workflow

**Use Case:** Complex file operations requiring multiple steps.

**User Query:**

> "Check if output.txt exists, and if not, create it with 'Initial content'"

## Step 1: Check existence

```bash
python scripts/file_exists.py "output.txt"
```

## Step 2: Conditionally create file (if doesn't exist)

```bash
python scripts/write_file.py "output.txt" "Initial content"
```

**Key Points:**

- Chain multiple filesystem operations for complex workflows
- Check file state before performing destructive operations (overwrites)
- Combine with other skills: read config -> process data -> write output
