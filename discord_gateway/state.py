"""Bot state management with proper encapsulation and lifecycle."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
import time
from typing import TypedDict


class ToolCallEntry(TypedDict, total=False):
    """Type definition for a single tool call with its response."""

    name: str
    args: dict
    response: dict | None


class TraceData(TypedDict, total=False):
    """Type definition for trace registry entries."""

    thoughts: str
    tools: list[ToolCallEntry]
    errors: list[str]


@dataclass
class BotState:
    """Centralized bot state with automatic eviction & lifecycle management."""

    # Message deduplication: OrderedDict for FIFO eviction
    processed_messages: OrderedDict[int, None] = field(
        default_factory=OrderedDict
    )
    max_processed_messages: int = 1000

    # Per-session locks with TTL
    session_locks: OrderedDict[str, tuple[asyncio.Lock, float]] = field(
        default_factory=OrderedDict
    )
    session_lock_ttl: float = 3600.0  # 1 hour
    session_lock_max: int = 100

    # Trace data for UI
    trace_registry: dict[str, TraceData] = field(default_factory=dict)

    # Background tasks
    running_tasks: set[asyncio.Task] = field(default_factory=set)

    def is_message_processed(self, message_id: int) -> bool:
        """Check if a message has already been processed.

        Args:
            message_id: The message ID to check.

        Returns:
            True if already processed.
        """
        return message_id in self.processed_messages

    def mark_message_processed(self, message_id: int) -> None:
        """Mark a message as processed with automatic FIFO eviction.

        Args:
            message_id: The message ID to mark.
        """
        self.processed_messages[message_id] = None
        if len(self.processed_messages) > self.max_processed_messages:
            self.processed_messages.popitem(last=False)

    def _evict_stale_locks(self, keep: str | None = None) -> None:
        """Remove expired session locks.

        A lock is only evicted when it is not currently held. Evicting
        a held lock would hand out a second, unrelated lock for the
        same session, letting two turns run concurrently. A held lock
        that is past its TTL is left in place and evicted on the next
        call after its holder releases it.
        """
        now = time.monotonic()
        expired = [
            sid
            for sid, (lock, last_used) in self.session_locks.items()
            if sid != keep
            and not lock.locked()
            and now - last_used > self.session_lock_ttl
        ]
        for sid in expired:
            del self.session_locks[sid]

        # Evict oldest unlocked lock if over max. If every lock is
        # held, keep them all rather than evicting a live turn; the
        # excess is cleaned up once a lock is released.
        while len(self.session_locks) > self.session_lock_max:
            for sid, (lock, _) in self.session_locks.items():
                if sid != keep and not lock.locked():
                    del self.session_locks[sid]
                    break
            else:
                break

    def get_session_lock(self, session_id: str) -> asyncio.Lock:
        """Get or create a session lock.

        Automatically evicts stale locks and enforces max concurrent limit.

        Args:
            session_id: The session identifier.

        Returns:
            An asyncio.Lock for the session.
        """
        self._evict_stale_locks()

        now = time.monotonic()
        if session_id not in self.session_locks:
            self.session_locks[session_id] = (asyncio.Lock(), now)

        lock, _ = self.session_locks[session_id]
        # Refresh the timestamp on every use, so the TTL is measured
        # from last use, not from when the lock was first created.
        self.session_locks[session_id] = (lock, now)
        self.session_locks.move_to_end(session_id)  # Mark as recently used
        # Enforce the max again now that this lock is in the dict:
        # the eviction at the top ran before insertion, so without
        # this the limit would only bite on the next call.
        self._evict_stale_locks(keep=session_id)
        return lock

    def store_trace(self, trace_id: str, data: TraceData) -> None:
        """Store trace data for UI retrieval.

        Args:
            trace_id: Unique trace identifier.
            data: The trace data to store.
        """
        self.trace_registry[trace_id] = data

    def get_trace(self, trace_id: str) -> TraceData | None:
        """Retrieve trace data by ID.

        Args:
            trace_id: The trace identifier.

        Returns:
            The trace data or None if not found.
        """
        return self.trace_registry.get(trace_id)

    def spawn_task(self, coro, name: str | None = None) -> asyncio.Task:
        """Create and track a background task.

        Args:
            coro: The coroutine to run.
            name: Optional task name for debugging.

        Returns:
            The created task.
        """
        task = asyncio.create_task(coro, name=name)
        self.running_tasks.add(task)
        task.add_done_callback(self.running_tasks.discard)
        return task

    async def shutdown(self) -> None:
        """Cancel all running tasks and cleanup state."""
        for task in list(self.running_tasks):
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self.running_tasks.clear()


# Global state instance - will be initialized in main.py
# This allows cogs to import the singleton but makes it replaceable for tests
_bot_state: BotState | None = None


def get_state() -> BotState:
    """Get the global bot state instance.

    Returns:
        The BotState singleton.

    Raises:
        RuntimeError: If state hasn't been initialized.
    """
    if _bot_state is None:
        raise RuntimeError("BotState not initialized. Call init_state() first.")
    return _bot_state


def init_state() -> BotState:
    """Initialize the global bot state.

    Returns:
        The initialized BotState.
    """
    global _bot_state  # noqa: PLW0603
    _bot_state = BotState()
    return _bot_state


def reset_state() -> BotState:
    """Reset the global state (useful for testing).

    Returns:
        The new BotState instance.
    """
    global _bot_state  # noqa: PLW0603
    _bot_state = BotState()
    return _bot_state
