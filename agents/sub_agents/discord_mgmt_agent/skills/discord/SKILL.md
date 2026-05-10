---
name: discord
description: Manage Discord interactions including messages, embeds, forms/modals, reactions, threads, and server management. Use when the user mentions Discord OR requests forms, profile setup, buttons, interactive components, or server actions.
metadata:
  version: 2.0.0
  adk_additional_tools:
    - add_reaction
    - send_channel_message
    - send_embed
    - send_message_with_components
    - send_modal_button
    - create_thread
    - get_channel_messages
    - get_message
    - edit_message
    - delete_message
    - get_guild_channels
    - get_guild_members
    - get_guild_roles
    - update_nickname
    - update_username
    - get_user
---

# Discord Management

This skill allows you to interact with the Discord platform directly using specialized tools. Use these tools to manage messages, gather server context, and maintain your identity.

## V2 Components (Rich Communication)

**Mandatory Preference**: You MUST prefer using V2 Components (`send_embed`, `send_message_with_components`, or `send_modal_button`) whenever you are presenting structured information, lists, or require user interaction. Do not use plain text for these scenarios.

### V2 Tools
- **`send_embed`**: Sends a rich embed.
  - *fields_json*: A JSON string list of fields. Example: `'[{"name": "Status", "value": "Online", "inline": true}]'`
- **`send_message_with_components`**: Sends a message with interactive **Buttons** or **Select Menus**.
  - *components_json*: A JSON string list of components.
    - *Button*: `{"type": 2, "label": "Label", "custom_id": "id", "style": 1}`
    - *Select Menu*: `{"type": 3, "custom_id": "id", "options": [{"label": "A", "value": "a"}]}`
- **`send_modal_button`**: Sends a button that, when clicked, opens a pop-up form (Modal).
  - *fields_json*: A JSON string list of input fields. Example: `'[{"label": "Name", "custom_id": "name", "style": 1, "required": true}]'`
- **`send_channel_message`**: Supports an optional `embed_json` string.

## Other Tools

### Message Management (CRUD)
- **`add_reaction`**: Adds an emoji reaction.
- **`get_channel_messages`**: Retrieves recent chat history.
- **`edit_message`**: Modifies a message previously sent by you. Supports `embed_json`.
- **`delete_message`**: Removes a message.
- **`get_message`**: Fetches a specific message by ID.

### Server (Guild) Information
- **`get_guild_channels`**, **`get_guild_members`**, **`get_guild_roles`**: Tools for gathering server-wide context.

### Identity & User Information
- **`update_nickname`**, **`update_username`**, **`get_user`**: Tools for managing identity and looking up user profiles.

## Best Practices

1. **JSON Strings**: For tools requiring JSON (e.g., `fields_json`, `embed_json`), you must provide a valid JSON-formatted string.
2. **Context Awareness**: Use the `Channel ID`, `Message ID`, and `Guild ID` provided in System Notes.
3. **Native Slash Commands**: The bot provides `/supportticket` (issue reporting) and `/onboarding` (profile setup). Acknowledge submissions from these commands contextually.
