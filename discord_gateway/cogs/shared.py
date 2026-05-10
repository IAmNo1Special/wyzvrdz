"""Shared utilities for Discord bot cogs.

This module provides decorators and helpers. State management has moved
to discord_gateway.state.BotState for proper encapsulation.
"""

import asyncio
from collections.abc import Callable, Coroutine
import functools
import logging
from typing import Any, TypeVar

import discord
from discord import ui

logger = logging.getLogger("discord_bot")

# Internal ADK function name for confirmations
ADK_CONFIRMATION_FUNC = "adk_request_confirmation"

T = TypeVar("T")


def with_typing_indicator[T](
    func: Callable[..., Coroutine[Any, Any, T]],
) -> Callable[..., Coroutine[Any, Any, T]]:
    """Decorator that shows typing indicator while the wrapped function runs.

    Works with both discord.Interaction and discord.Message contexts.
    The first positional argument must be the interaction or message.

    Example:
        @with_typing_indicator
        async def process_message(message: discord.Message, content: str):
            # User sees "Bot is typing..." while this runs
            await long_running_task()
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        if not args:
            return await func(*args, **kwargs)

        ctx = args[0]
        channel = None

        # Try to extract channel from different context types
        if hasattr(ctx, "channel"):
            channel = ctx.channel
        elif isinstance(ctx, (discord.Message, discord.Interaction)):  # type: ignore[misc]
            channel = ctx.channel

        if channel and hasattr(channel, "typing"):
            async with channel.typing():
                return await func(*args, **kwargs)
        else:
            return await func(*args, **kwargs)

    return wrapper


def spawn_background_task(
    coro: Coroutine[Any, Any, Any],
    name: str | None = None,
    on_error: Callable[[Exception], Coroutine[Any, Any, Any]] | None = None,
) -> asyncio.Task:
    """Create a background task with automatic error handling and cleanup.

    Args:
        coro: The coroutine to run.
        name: Optional task name for debugging.
        on_error: Optional error handler callback.

    Returns:
        The created task.
    """

    async def wrapper() -> None:
        try:
            await coro
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if on_error:
                await on_error(e)
            else:
                logger.error(
                    "Background task %s failed: %s", name or "unknown", e
                )

    task = asyncio.create_task(wrapper(), name=name)
    return task


def build_text_view(
    content: str, *, accent_color: int | None = None
) -> ui.LayoutView:
    """Build a V2 LayoutView containing a single Container with TextDisplay.

    In Components V2, plain ``content`` fields are disabled when the
    ``IS_COMPONENTS_V2`` flag is set.  All visible text must be expressed
    through ``TextDisplay`` components inside a ``Container``.

    Args:
        content: The markdown-formatted text to display.
        accent_color: Optional accent color for the container.

    Returns:
        A ``ui.LayoutView`` ready to be passed to ``send(view=...)``.
    """
    view = ui.LayoutView()
    text_display = ui.TextDisplay(content)
    container = ui.Container(text_display, accent_color=accent_color)
    view.add_item(container)
    return view
