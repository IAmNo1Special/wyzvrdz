"""ADK-compatible tool wrappers around DiscordAPIClient.

These standalone async functions are compatible with
google.adk.tools.FunctionTool
while internally using the DiscordAPIClient class for all operations.
"""

from __future__ import annotations

import json
from typing import Any

from .client import DiscordAPIClient, Embed
from .exceptions import DiscordAPIError, PermissionError

# Global client instance - initialized lazily
_client: DiscordAPIClient | None = None


def _get_client() -> DiscordAPIClient:
    """Get or create the global client instance."""
    global _client  # noqa: PLW0603
    if _client is None:
        _client = DiscordAPIClient()
    return _client


def _format_error(e: DiscordAPIError) -> dict[str, Any]:
    """Format exception as dict for ADK compatibility."""
    return {
        "status": "error",
        "code": getattr(e, "status_code", 0),
        "error": str(e),
    }


# --- Message Operations ---


async def send_message(
    channel_id: str,
    content: str,
    embed_json: str | None = None,
    reply_to_message_id: str | None = None,
) -> dict[str, Any]:
    """Send a message to a Discord channel.

    Args:
        channel_id: The ID of the channel to send to.
        content: The message text content.
        embed_json: Optional JSON string of an embed object.
        reply_to_message_id: Optional message ID to reply to.

    Returns:
        The sent message as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        embed = None
        if embed_json:
            data = json.loads(embed_json)
            embed = Embed(
                title=data.get("title", ""),
                description=data.get("description", ""),
                color=data.get("color", 3447003),
                fields=data.get("fields", []),
            )
        msg = await client.send_message(
            channel_id, content, embed=embed, reply_to=reply_to_message_id
        )
        return {"status": "success", "message": msg.raw_data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def send_embed(  # noqa: PLR0913
    channel_id: str,
    title: str,
    description: str,
    color: int = 3447003,
    fields_json: str | None = None,
    reply_to_message_id: str | None = None,
) -> dict[str, Any]:
    """Send a rich embed message to a Discord channel.

    Args:
        channel_id: The ID of the channel to send to.
        title: The embed title.
        description: The embed description.
        color: The color code (default: blurple).
        fields_json: Optional JSON string of field list.
        reply_to_message_id: Optional message ID to reply to.

    Returns:
        The sent message as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        fields = json.loads(fields_json) if fields_json else []
        msg = await client.send_embed(
            channel_id, title, description, color, fields, reply_to_message_id
        )
        return {"status": "success", "message": msg.raw_data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def edit_message(
    channel_id: str,
    message_id: str,
    content: str,
    embed_json: str | None = None,
) -> dict[str, Any]:
    """Edit a previously sent message.

    Args:
        channel_id: Channel containing the message.
        message_id: Message to edit.
        content: New text content.
        embed_json: Optional new embed JSON.

    Returns:
        The updated message as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        embed = None
        if embed_json:
            data = json.loads(embed_json)
            embed = Embed(
                title=data.get("title", ""),
                description=data.get("description", ""),
                color=data.get("color", 3447003),
                fields=data.get("fields", []),
            )
        msg = await client.edit_message(channel_id, message_id, content, embed)
        return {"status": "success", "message": msg.raw_data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def delete_message(channel_id: str, message_id: str) -> dict[str, Any]:
    """Delete a message.

    Args:
        channel_id: Channel containing the message.
        message_id: Message to delete.

    Returns:
        Success status dict, or error dict on failure.
    """
    client = _get_client()
    try:
        await client.delete_message(channel_id, message_id)
        return {"status": "success"}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_message(channel_id: str, message_id: str) -> dict[str, Any]:
    """Fetch a specific message.

    Args:
        channel_id: Channel containing the message.
        message_id: Message to fetch.

    Returns:
        The message as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        msg = await client.get_message(channel_id, message_id)
        return {"status": "success", "message": msg.raw_data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_channel_messages(
    channel_id: str, limit: int = 10
) -> dict[str, Any]:
    """Fetch recent messages from a channel.

    Args:
        channel_id: Channel to fetch from.
        limit: Max messages (max 100).

    Returns:
        List of messages as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        messages = await client.get_channel_messages(channel_id, limit)
        return {
            "status": "success",
            "messages": [m.raw_data for m in messages],
        }
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Reaction Operations ---


async def add_reaction(
    channel_id: str, message_id: str, emoji: str
) -> dict[str, Any]:
    """Add an emoji reaction to a message.

    Args:
        channel_id: Channel containing the message.
        message_id: Message to react to.
        emoji: Emoji to add (Unicode or :name:id format).

    Returns:
        Success status dict, or error dict on failure.
    """
    client = _get_client()
    try:
        await client.add_reaction(channel_id, message_id, emoji)
        return {"status": "success"}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Thread Operations ---


async def create_thread(
    channel_id: str, message_id: str, name: str
) -> dict[str, Any]:
    """Create a public thread from a message.

    Args:
        channel_id: Channel containing the message.
        message_id: Message to start thread from.
        name: Thread name.

    Returns:
        Thread channel data as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        data = await client.create_thread(channel_id, message_id, name)
        return {"status": "success", "thread": data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Guild Operations ---


async def get_guild_channels(guild_id: str) -> dict[str, Any]:
    """List all channels in a server.

    Args:
        guild_id: Guild to list channels for.

    Returns:
        List of channels as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        channels = await client.get_guild_channels(guild_id)
        return {"status": "success", "channels": channels}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_guild_members(guild_id: str, limit: int = 50) -> dict[str, Any]:
    """List members in a server.

    Args:
        guild_id: Guild to list members for.
        limit: Max members to fetch.

    Returns:
        List of members as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        members = await client.get_guild_members(guild_id, limit)
        return {"status": "success", "members": members}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_guild_roles(guild_id: str) -> dict[str, Any]:
    """List roles in a server.

    Args:
        guild_id: Guild to list roles for.

    Returns:
        List of roles as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        roles = await client.get_guild_roles(guild_id)
        return {"status": "success", "roles": roles}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Bot Identity ---


async def update_nickname(guild_id: str, nickname: str) -> dict[str, Any]:
    """Change the bot's nickname in a server.

    Args:
        guild_id: Guild to change nickname in.
        nickname: New nickname.

    Returns:
        Updated member data as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        data = await client.update_nickname(guild_id, nickname)
        return {"status": "success", "member": data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def update_username(username: str) -> dict[str, Any]:
    """Change the bot's global username.

    Args:
        username: New username.

    Returns:
        Updated user data as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        data = await client.update_username(username)
        return {"status": "success", "user": data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_user(user_id: str) -> dict[str, Any]:
    """Fetch a user by ID.

    Args:
        user_id: User to fetch.

    Returns:
        User data as dict, or error dict on failure.
    """
    client = _get_client()
    try:
        data = await client.get_user(user_id)
        return {"status": "success", "user": data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Component Operations ---


async def send_message_with_components(
    channel_id: str,
    content: str,
    components_json: str,
    reply_to_message_id: str | None = None,
) -> dict[str, Any]:
    """Send a message with interactive components.

    Args:
        channel_id: Target channel.
        content: Message text.
        components_json: JSON string of component list.
        reply_to_message_id: Optional message ID to reply to.

    Returns:
        The sent message as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        components = json.loads(components_json)
        msg = await client.send_message_with_components(
            channel_id, content, components, reply_to_message_id
        )
        return {"status": "success", "message": msg.raw_data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def send_modal_button(  # noqa: PLR0913
    channel_id: str,
    title: str,
    custom_id: str,
    button_label: str,
    fields_json: str,
    reply_to_message_id: str | None = None,
) -> dict[str, Any]:
    """Send a button that opens a modal form when clicked.

    Args:
        channel_id: Target channel.
        title: Modal form title.
        custom_id: Unique identifier for this modal.
        button_label: Text on the trigger button.
        fields_json: JSON string of field definitions.
        reply_to_message_id: Optional message ID to reply to.

    Returns:
        The sent message as a dict, or error dict on failure.
    """
    client = _get_client()
    try:
        fields = json.loads(fields_json)
        msg = await client.send_modal_button(
            channel_id,
            title,
            custom_id,
            button_label,
            fields,
            reply_to_message_id,
        )
        return {"status": "success", "message": msg.raw_data}
    except PermissionError as e:
        return _format_error(e)
    except Exception as e:
        return {"status": "error", "error": str(e)}
