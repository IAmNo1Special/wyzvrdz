"""Discord API client with connection pooling, retry logic, and errors.

Provides a robust async HTTP client for Discord API operations.
"""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
import logging
from os import getenv
import time
from typing import TYPE_CHECKING, Any

import aiohttp

from .exceptions import (
    DiscordAPIError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger("discord_tools")

DISCORD_API_BASE = "https://discord.com/api/v10"

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_RATE_LIMIT = 429
HTTP_SERVER_ERROR_THRESHOLD = 500

# URL parsing constants
URL_PATH_COMPONENTS_MIN = 2

# Retry configuration
MAX_RETRIES = 3
RATE_LIMIT_BASE_DELAY = 1.0

# Permission error mapping
_PERMISSION_MESSAGES: Mapping[int | str, str] = {
    "SEND_MESSAGES": (
        "I don't have permission to send messages in that channel."
    ),
    "EMBED_LINKS": "I don't have permission to embed links in that channel.",
    "MANAGE_MESSAGES": (
        "I don't have permission to manage messages in that channel."
    ),
    "ADD_REACTIONS": (
        "I don't have permission to add reactions in that channel."
    ),
    "MANAGE_CHANNELS": (
        "I don't have permission to manage channels in that server."
    ),
    "MANAGE_ROLES": "I don't have permission to manage roles in that server.",
    "MANAGE_NICKNAMES": (
        "I don't have permission to change nicknames in that server."
    ),
    "CHANGE_NICKNAME": "I don't have permission to change my own nickname.",
    "CREATE_THREADS": (
        "I don't have permission to create threads in that channel."
    ),
    "VIEW_CHANNEL": "I don't have permission to view that channel.",
    "READ_MESSAGE_HISTORY": (
        "I don't have permission to read message history in that channel."
    ),
}

# Embed limits
_EMBED_FIELD_MAX_NAME = 256
_EMBED_FIELD_MAX_VALUE = 1024
_EMBED_MAX_FIELDS = 25
_EMBED_MAX_TITLE = 256
_EMBED_MAX_DESCRIPTION = 4096
_EMBED_MAX_TOTAL_CHARS = 6000


@dataclass
class Embed:
    """Discord embed builder with validation."""

    title: str
    description: str
    color: int = 3447003
    fields: list[dict[str, Any]] = field(default_factory=list)
    footer_text: str | None = None
    author_name: str | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to Discord API format with length validation."""
        embed: dict[str, Any] = {
            "title": self.title[:_EMBED_MAX_TITLE],
            "description": self.description[:_EMBED_MAX_DESCRIPTION],
            "color": self.color,
        }

        if self.url:
            embed["url"] = self.url

        if self.author_name:
            embed["author"] = {"name": self.author_name[:_EMBED_MAX_TITLE]}

        if self.footer_text:
            embed["footer"] = {"text": self.footer_text[:2048]}

        if self.fields:
            fields = self.fields[:_EMBED_MAX_FIELDS]
            validated = [
                {
                    "name": str(f.get("name", ""))[:_EMBED_FIELD_MAX_NAME],
                    "value": str(f.get("value", ""))[:_EMBED_FIELD_MAX_VALUE],
                    "inline": bool(f.get("inline", False)),
                }
                for f in fields
            ]
            embed["fields"] = validated

        # Rough total length check
        total = len(embed.get("title", "")) + len(embed.get("description", ""))
        for f in embed.get("fields", []):
            total += len(f["name"]) + len(f["value"])
        if total > _EMBED_MAX_TOTAL_CHARS:
            embed["description"] = embed["description"][
                : _EMBED_MAX_DESCRIPTION - (total - _EMBED_MAX_TOTAL_CHARS)
            ]

        return embed


@dataclass
class Message:
    """Discord message response."""

    id: str
    channel_id: str
    content: str
    embeds: list[dict] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)


class _ExpiringModalRegistry(OrderedDict):
    """OrderedDict that auto-evicts entries older than TTL."""

    def __init__(self, ttl: int = 3600):  # 1 hour default
        super().__init__()
        self._ttl = ttl

    def __setitem__(self, key: str, value: dict) -> None:
        value["_created_at"] = time.monotonic()
        super().__setitem__(key, value)
        self._evict_expired()

    def __getitem__(self, key: str) -> dict:
        self._evict_expired()
        return super().__getitem__(key)

    def get(self, key: str, default: dict | None = None) -> dict | None:
        """Get with fallback, does not evict."""
        return super().get(key, default)

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [
            k
            for k, v in self.items()
            if now - v.get("_created_at", now) > self._ttl
        ]
        for k in expired:
            del self[k]


class DiscordAPIClient:
    """Async Discord API client with connection pooling and retry logic.

    Multiple instances share a single aiohttp session for connection pooling,
    making this safe to use across multiple cogs.
    """

    # Class-level shared session for connection pooling across instances
    _shared_session: aiohttp.ClientSession | None = None
    _session_ref_count: int = 0
    _session_lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, token: str | None = None):
        """Initialize the client.

        Args:
            token: Discord bot token. Defaults to DISCORD_BOT_TOKEN env var.
        """
        self._token = token or getenv("DISCORD_BOT_TOKEN", "")
        self._modal_registry = _ExpiringModalRegistry()

    async def __aenter__(self) -> DiscordAPIClient:
        """Enter async context, create session."""
        await self.connect()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context, close session."""
        await self.close()

    @property
    def _session(self) -> aiohttp.ClientSession | None:
        """Get the shared session."""
        return DiscordAPIClient._shared_session

    async def connect(self) -> None:
        """Initialize the shared HTTP session (reference counted)."""
        async with DiscordAPIClient._session_lock:
            if (
                DiscordAPIClient._shared_session is None
                or DiscordAPIClient._shared_session.closed
            ):
                DiscordAPIClient._shared_session = aiohttp.ClientSession()
            DiscordAPIClient._session_ref_count += 1

    async def close(self) -> None:
        """Close the shared HTTP session (reference counted).

        Only actually closes when all client instances are closed.
        """
        async with DiscordAPIClient._session_lock:
            DiscordAPIClient._session_ref_count = max(
                0, DiscordAPIClient._session_ref_count - 1
            )
            if (
                DiscordAPIClient._session_ref_count == 0
                and DiscordAPIClient._shared_session
            ):
                if not DiscordAPIClient._shared_session.closed:
                    await DiscordAPIClient._shared_session.close()
                DiscordAPIClient._shared_session = None

    async def _request(  # noqa: PLR0912
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict:
        """Make authenticated request with retry logic.

        Args:
            method: HTTP method.
            endpoint: API endpoint (starting with /).
            data: Optional JSON payload.

        Returns:
            Parsed JSON response.

        Raises:
            DiscordAPIError: On API errors.
        """
        if not self._token:
            raise DiscordAPIError("Discord bot token not configured")

        if self._session is None:
            await self.connect()

        url = f"{DISCORD_API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bot {self._token}",
            "User-Agent": "ZionAgent",
            "Content-Type": "application/json",
        }

        for attempt in range(MAX_RETRIES + 1):
            async with self._session.request(  # type: ignore[union-attr]
                method, url, headers=headers, json=data
            ) as resp:
                if resp.status in (HTTP_OK, HTTP_CREATED):
                    return await resp.json()

                if resp.status == HTTP_NO_CONTENT:
                    return {"status": "success"}

                if resp.status == HTTP_RATE_LIMIT:
                    if attempt < MAX_RETRIES:
                        try:
                            body = await resp.json()
                            retry_after = float(
                                body.get("retry_after", RATE_LIMIT_BASE_DELAY)
                            )
                        except Exception:
                            retry_after = RATE_LIMIT_BASE_DELAY
                        logger.warning(
                            "Rate limited on %s %s, retrying after %.1fs",
                            method,
                            endpoint,
                            retry_after,
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    raise RateLimitError(retry_after=RATE_LIMIT_BASE_DELAY)

                if resp.status == HTTP_FORBIDDEN:
                    raw = await self._parse_error(resp)
                    msg = self._interpret_forbidden(raw)
                    raise PermissionError("unknown", msg)

                if resp.status == HTTP_NOT_FOUND:
                    resource = endpoint.split("/")[1]  # e.g., "channels"
                    parts = endpoint.split("/")
                    resource_id = "unknown"
                    if len(parts) > URL_PATH_COMPONENTS_MIN:
                        resource_id = parts[2]
                    raise NotFoundError(resource, resource_id)

                if resp.status == HTTP_BAD_REQUEST:
                    raw = await self._parse_error(resp)
                    raise ValidationError(
                        "Request validation failed",
                        errors=raw if isinstance(raw, dict) else {},
                    )

                if resp.status >= HTTP_SERVER_ERROR_THRESHOLD:
                    if attempt < MAX_RETRIES:
                        delay = RATE_LIMIT_BASE_DELAY * (2**attempt)
                        logger.warning(
                            "Server error %d on %s %s, retrying in %.1fs",
                            resp.status,
                            method,
                            endpoint,
                            delay,
                        )
                        await asyncio.sleep(delay)
                        continue
                    raise ServerError(resp.status)

                # Other client errors
                raw = await self._parse_error(resp)
                raise DiscordAPIError(
                    f"Discord API error: {raw}",
                    status_code=resp.status,
                )

        raise DiscordAPIError("Max retries exceeded")

    async def _parse_error(self, resp: aiohttp.ClientResponse) -> dict | str:
        """Parse error response body."""
        try:
            return await resp.json()
        except Exception:
            return await resp.text()

    def _interpret_forbidden(self, error_data: dict | str) -> str:
        """Produce human-readable permission error."""
        if isinstance(error_data, dict):
            errors = error_data.get("errors", {})
            for field_errors in errors.values():
                for err_obj in field_errors.get("_errors", []):
                    code = err_obj.get("code", "")
                    if code in _PERMISSION_MESSAGES:
                        return _PERMISSION_MESSAGES[code]
            code = error_data.get("code", "")
            if code in _PERMISSION_MESSAGES:
                return _PERMISSION_MESSAGES[code]
        return "I don't have the required permission to perform this action."

    # --- Message Operations ---

    async def send_message(
        self,
        channel_id: str,
        content: str,
        embed: Embed | None = None,
        reply_to: str | None = None,
    ) -> Message:
        """Send a message to a channel.

        Args:
            channel_id: Target channel ID.
            content: Message text content.
            embed: Optional embed to include.
            reply_to: Optional message ID to reply to.

        Returns:
            The sent message.
        """
        payload: dict[str, Any] = {"content": content}
        if embed:
            payload["embeds"] = [embed.to_dict()]
        if reply_to:
            payload["message_reference"] = {"message_id": reply_to}

        data = await self._request(
            "POST", f"/channels/{channel_id}/messages", payload
        )
        return Message(
            id=data["id"],
            channel_id=data["channel_id"],
            content=data.get("content", ""),
            embeds=data.get("embeds", []),
            raw_data=data,
        )

    async def send_embed(  # noqa: PLR0913
        self,
        channel_id: str,
        title: str,
        description: str,
        color: int = 3447003,
        fields: list[dict] | None = None,
        reply_to: str | None = None,
    ) -> Message:
        """Send an embed message (convenience method).

        Args:
            channel_id: Target channel ID.
            title: Embed title.
            description: Embed description.
            color: Color code (default: blurple).
            fields: Optional field list.
            reply_to: Optional message ID to reply to.

        Returns:
            The sent message.
        """
        embed = Embed(
            title=title,
            description=description,
            color=color,
            fields=fields or [],
        )
        return await self.send_message(
            channel_id, "", embed=embed, reply_to=reply_to
        )

    async def edit_message(
        self,
        channel_id: str,
        message_id: str,
        content: str,
        embed: Embed | None = None,
    ) -> Message:
        """Edit a previously sent message.

        Args:
            channel_id: Channel containing the message.
            message_id: Message to edit.
            content: New text content.
            embed: Optional new embed.

        Returns:
            The updated message.
        """
        payload: dict[str, Any] = {"content": content}
        if embed:
            payload["embeds"] = [embed.to_dict()]

        data = await self._request(
            "PATCH",
            f"/channels/{channel_id}/messages/{message_id}",
            payload,
        )
        return Message(
            id=data["id"],
            channel_id=data["channel_id"],
            content=data.get("content", ""),
            embeds=data.get("embeds", []),
            raw_data=data,
        )

    async def delete_message(self, channel_id: str, message_id: str) -> None:
        """Delete a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Message to delete.
        """
        await self._request(
            "DELETE",
            f"/channels/{channel_id}/messages/{message_id}",
        )

    async def get_message(self, channel_id: str, message_id: str) -> Message:
        """Fetch a specific message.

        Args:
            channel_id: Channel containing the message.
            message_id: Message to fetch.

        Returns:
            The message.
        """
        data = await self._request(
            "GET",
            f"/channels/{channel_id}/messages/{message_id}",
        )
        return Message(
            id=data["id"],
            channel_id=data["channel_id"],
            content=data.get("content", ""),
            embeds=data.get("embeds", []),
            raw_data=data,
        )

    async def get_channel_messages(
        self, channel_id: str, limit: int = 10
    ) -> list[Message]:
        """Fetch recent messages from a channel.

        Args:
            channel_id: Channel to fetch from.
            limit: Max messages (max 100).

        Returns:
            List of messages (newest first).
        """
        data = await self._request(
            "GET",
            f"/channels/{channel_id}/messages?limit={min(limit, 100)}",
        )
        return [
            Message(
                id=m["id"],
                channel_id=m["channel_id"],
                content=m.get("content", ""),
                embeds=m.get("embeds", []),
                raw_data=m,
            )
            for m in data
        ]

    # --- Reaction Operations ---

    async def add_reaction(
        self, channel_id: str, message_id: str, emoji: str
    ) -> None:
        """Add an emoji reaction to a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Message to react to.
            emoji: Emoji to add (Unicode or custom emoji format).
        """
        # URL-encode emoji for the endpoint
        encoded_emoji = emoji.replace(":", "%3A") if ":" in emoji else emoji
        await self._request(
            "PUT",
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me",
        )

    # --- Thread Operations ---

    async def create_thread(
        self, channel_id: str, message_id: str, name: str
    ) -> dict:
        """Create a public thread from a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Message to start thread from.
            name: Thread name.

        Returns:
            Thread channel data.
        """
        return await self._request(
            "POST",
            f"/channels/{channel_id}/messages/{message_id}/threads",
            {"name": name},
        )

    # --- Guild Operations ---

    async def get_guild_channels(self, guild_id: str) -> list[dict]:
        """List all channels in a guild.

        Args:
            guild_id: Guild to list channels for.

        Returns:
            List of channel objects.
        """
        return await self._request("GET", f"/guilds/{guild_id}/channels")

    async def get_guild_members(
        self, guild_id: str, limit: int = 50
    ) -> list[dict]:
        """List members in a guild.

        Args:
            guild_id: Guild to list members for.
            limit: Max members to fetch.

        Returns:
            List of member objects.
        """
        return await self._request(
            "GET",
            f"/guilds/{guild_id}/members?limit={limit}",
        )

    async def get_guild_roles(self, guild_id: str) -> list[dict]:
        """List roles in a guild.

        Args:
            guild_id: Guild to list roles for.

        Returns:
            List of role objects.
        """
        return await self._request("GET", f"/guilds/{guild_id}/roles")

    # --- Bot Identity ---

    async def update_nickname(self, guild_id: str, nickname: str) -> dict:
        """Change the bot's nickname in a guild.

        Args:
            guild_id: Guild to change nickname in.
            nickname: New nickname.

        Returns:
            Updated member data.
        """
        return await self._request(
            "PATCH",
            f"/guilds/{guild_id}/members/@me",
            {"nick": nickname},
        )

    async def update_username(self, username: str) -> dict:
        """Change the bot's global username.

        Args:
            username: New username.

        Returns:
            Updated user data.
        """
        return await self._request(
            "PATCH",
            "/users/@me",
            {"username": username},
        )

    async def get_user(self, user_id: str) -> dict:
        """Fetch a user by ID.

        Args:
            user_id: User to fetch.

        Returns:
            User object.
        """
        return await self._request("GET", f"/users/{user_id}")

    # --- Component Operations ---

    async def send_message_with_components(
        self,
        channel_id: str,
        content: str,
        components: list[dict],
        reply_to: str | None = None,
    ) -> Message:
        """Send a message with interactive components.

        Args:
            channel_id: Target channel.
            content: Message text.
            components: List of component dicts.
            reply_to: Optional message ID to reply to.

        Returns:
            The sent message.
        """
        payload: dict[str, Any] = {
            "content": content,
            "components": [{"type": 1, "components": components}],
        }
        if reply_to:
            payload["message_reference"] = {"message_id": reply_to}

        data = await self._request(
            "POST", f"/channels/{channel_id}/messages", payload
        )
        return Message(
            id=data["id"],
            channel_id=data["channel_id"],
            content=data.get("content", ""),
            embeds=data.get("embeds", []),
            raw_data=data,
        )

    async def send_modal_button(  # noqa: PLR0913
        self,
        channel_id: str,
        title: str,
        custom_id: str,
        button_label: str,
        fields: list[dict],
        reply_to: str | None = None,
    ) -> Message:
        """Send a button that opens a modal form when clicked.

        Args:
            channel_id: Target channel.
            title: Modal form title.
            custom_id: Unique identifier for this modal schema.
            button_label: Text on the trigger button.
            fields: List of field definitions.
            reply_to: Optional message ID to reply to.

        Returns:
            The sent message.
        """
        # Store modal schema in registry
        self._modal_registry[custom_id] = {"title": title, "fields": fields}

        button = {
            "type": 2,
            "style": 1,
            "label": button_label,
            "custom_id": f"modal_trigger:{custom_id}",
        }

        return await self.send_message_with_components(
            channel_id,
            f"Click the button below to open the '{title}' form.",
            [button],
            reply_to=reply_to,
        )

    def get_modal_schema(self, custom_id: str) -> dict | None:
        """Retrieve a modal schema from the registry.

        Args:
            custom_id: The modal's custom ID.

        Returns:
            The schema dict or None if expired/not found.
        """
        try:
            return self._modal_registry[custom_id]
        except KeyError:
            return None
