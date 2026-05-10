---
name: compendium
description: Manage the INTERNAL Wyzvrd Compendium knowledge base only. Use for personal wiki pages, notes, and ingested files. Do NOT use for external web searches (Wikipedia, Google, etc.) - use web_research_agent for external knowledge.
metadata:
  adk_additional_tools:
    - web_research_agent
---

# Compendium Management Instructions

You are the sole maintainer of the Wyzvrd Compendium (your personal knowledge base). Your goal is to ensure information is captured accurately, categorized logically, and linked semantically to form a robust knowledge graph.
**When to use**: Queries about "my compendium", "personal wiki", ingesting files from Desktop, or managing internal notes.
**When NOT to use**: External searches like "Wikipedia", "Google", "look up online" - those need web_research_agent.

## Core Workflows

### 1. Accessing Known Knowledge

When you need to get information from the compendium:

1. **Search First**: Run `scripts/search_compendium.py` to see if a page already exists.
1. **Read**: Use `scripts/read_compendium_file.py` to read the contents of a specific page.

### 2. Capturing New Knowledge

When you learn something new (either from the user or by reading a raw source):

1. **Search First**: Run `scripts/search_compendium.py` to see if a page already exists.
1. **Create/Update**:
   - Use `scripts/write_compendium_file.py` to create a new page or overwrite an existing one.
   - Use `scripts/append_to_compendium_file.py` to add new sections without overwriting.
1. **Format Entry**: Always run `python scripts/format_compendium_files.py --file <filename>` immediately after creating or updating a page to ensure consistent formatting.
1. **Log the Change**: Always run `scripts/write_compendium_file.py log.md ...` to document the update.
1. **Update Visualization**: Run `scripts/update_compendium_visualization.py` immediately after any structure change.

### 3. Ingesting Raw Sources

Raw knowledge files are located on the user's Desktop.

1. **List Sources**: Run `python scripts/ingest_compendium_source.py list`.
1. **Check Size**: Run `python scripts/ingest_compendium_source.py info <filename>`.
1. **Read in Chunks**: If a file is large, read it section-by-section using `python scripts/ingest_compendium_source.py read <filename> <index>`.

### 4. Maintaining the Knowledge Graph (Obsidian Optimized)

Every page MUST follow these standards for maximum compatibility with Obsidian and the Dataview plugin:

1. **H1 for Titles**: Every file must start with a single `# Title` heading.
1. **No Multiple H1s**: Never use `#` for sections; use `##`, `###`, etc. Multiple H1s trigger linting errors (MD025).
1. **YAML Frontmatter**: Always include `category`, `tags`, and `updated: 'YYYY-MM-DD'`.
1. **Wikilinks**: Use `[[Page Name]]` for all internal links. For aliases, use `[[Page Name|Alias]]`.
1. **Semantic Relationships**: Use the format `Relationship:: [[Target Name]]` on a new line or within a list.
1. **Callouts**: Use Obsidian callouts `> [!INFO]` for summaries or key takeaways.
1. **Blank Line Discipline**:
   - Exactly ONE blank line before and after every heading (MD022).
   - Exactly ONE blank line before and after every list (MD032).
   - Exactly ONE blank line between the frontmatter and the title.
1. **Automatic Formatting**: Always run `python scripts/format_compendium_files.py --file <filename>` after any edit.

## Available Scripts

- **`scripts/search_compendium.py <query>`**: Full-text search across all MD files.
- **`scripts/read_compendium_file.py <filename>`**: Retrieve the contents of a specific page.
- **`scripts/write_compendium_file.py <filename> <content>`**: Save or overwrite a page.
- **`scripts/append_to_compendium_file.py <filename> <content> [--line <L>]`**: Add content to a page. Optional `--line` (or `-L`) specifies a 1-indexed line number to insert at; otherwise, it appends to the end.
- **`scripts/remove_compendium_line.py <filename> <line>`**: Permanently remove a specific 1-indexed line from a page.
- **`scripts/get_compendium_stats.py`**: Get a summary of page counts and last log entry.
- **`scripts/get_current_timestamp.py`**: Retrieve the current date and time (essential for logging).
- **`scripts/update_compendium_visualization.py`**: Refreshes the Mermaid graph in `index.md`.
- **`scripts/format_compendium_files.py [--file <filename>]`**: Formats all compendium files or a specific file using `mdformat`. Run this after every write/update.
- **`scripts/ingest_compendium_source.py <command> ...`**: Manage raw knowledge files (commands: `list`, `info`, `read`).

## RULES YOU MUST FOLLOW

See [references/rules.md](references/rules.md) for ALL Markdown formatting/linting rules that you MUST follow when writing or updating compendium pages.
