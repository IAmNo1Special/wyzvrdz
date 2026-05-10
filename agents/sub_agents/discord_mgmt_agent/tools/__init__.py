"""Discord tools package.

New code should use DiscordAPIClient class. ADK tools use wrapper functions.
"""

from .client import DiscordAPIClient, Embed, Message
from .exceptions import (
    DiscordAPIError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .tool_wrappers import (
    add_reaction,
    create_thread,
    delete_message,
    edit_message,
    get_channel_messages,
    get_guild_channels,
    get_guild_members,
    get_guild_roles,
    get_message,
    get_user,
    send_embed,
    send_message,
    send_message_with_components,
    send_modal_button,
    update_nickname,
    update_username,
)

__all__ = [
    # Client and data classes
    "DiscordAPIClient",
    "Embed",
    "Message",
    # Exceptions
    "DiscordAPIError",
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
    # ADK wrapper functions
    "add_reaction",
    "create_thread",
    "delete_message",
    "edit_message",
    "get_channel_messages",
    "get_guild_channels",
    "get_guild_members",
    "get_guild_roles",
    "get_message",
    "get_user",
    "send_embed",
    "send_message",
    "send_message_with_components",
    "send_modal_button",
    "update_nickname",
    "update_username",
]
