# Wyzvrdz

Wyzvrdz is an advanced, multi-agent AI system utilizing the **Google Agent Development Kit (ADK)**. It operates primarily as a rich, interactive Discord bot, bridging the asynchronous streaming capabilities of ADK agents into dynamic Discord UI components.

## Key Features

- **Rich Discord Integration**: Goes beyond a standard text bot by acting as a dynamic, stateful UI client. It streams granular ADK lifecycle events (agent thoughts, active tool execution, and non-fatal errors) directly into mutable Discord UI views.
- **Interactive Tool Confirmations**: Seamlessly handles ADK's protected tool confirmations via interactive Discord UI buttons, pausing execution until a human explicitly approves or declines an action.
- **Active Skill Routing (MCP-Zero Pattern)**: Instead of injecting a massive, token-heavy XML catalog of all available skills into the LLM's system prompt, the system utilizes **Full Active Discovery**. The agent queries a Moss (`moss-minilm`) embedding router with a desired domain and capability, dynamically fetching and loading specialized skills only when needed.
- **Multi-Agent Architecture**:
  - **Root Agent**: Coordinations operations and manages the core "Soul" identity.
  - **Discord Management Agent**: Specialized for interacting with the Discord API.
  - **Compendium Management Agent**: Maintains an internal, personal knowledge base.
  - **Web Research Agent**: Dedicated to external information gathering.

## Architecture Highlights

1. **Discord Gateway (`discord_gateway/`)**: Connects to the Discord websocket, manages transient bot state (with async session locks and TTL eviction), deduplicates messages, and routes events. It provides a highly robust, rate-limit-aware async HTTP client for executing Discord API calls safely.
2. **Agent Engine (`agents/`)**: Handles the core LLM orchestration. The root agent delegates complex logic to specialized sub-agents.
3. **Skill Discovery (`agents/routing/`)**: Uses two-stage semantic vector matching (Domain Index and Capability Index) with cubic scoring to accurately match agent requests to the correct capabilities, preventing prompt bloat and keeping the agent highly focused.

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Required API Keys:
  - `DISCORD_BOT_TOKEN`: For the Discord Gateway.
  - `MOSS_PROJECT_ID` & `MOSS_PROJECT_KEY`: For semantic skill routing.
  - LLM API Keys (e.g., `GEMINI_API_KEY` for Google models, or configure an Ollama URL for local execution).

## Installation & Setup

1. **Install dependencies** using `uv`:

   ```bash
   uv sync
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the project root containing your necessary API keys:

   ```env
   DISCORD_BOT_TOKEN=your_token_here
   MOSS_PROJECT_ID=your_moss_project_id
   MOSS_PROJECT_KEY=your_moss_project_key
   ```

3. **Run the Application**:
   Start the application and Discord bot via the main entrypoint:

   ```bash
   uv run .
   ```
