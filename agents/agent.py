"""Wyzvrd instance for ADK web testing."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from .services.cron import CronService
from .wyzvrd_factory import WyzvrdFactory

if TYPE_CHECKING:
    from google.adk import Runner
    from google.adk.agents import BaseAgent
    from starlette.applications import Starlette

logger = logging.getLogger(__name__)

# Lazy initialization to avoid eager module-level execution
_runner: Runner | None = None
_a2a_app: Starlette | None = None
_cron_service: CronService | None = None


def _start_cron_service(runner: Runner) -> None:
    """Start the cron service in a background task if event loop is running."""
    global _cron_service  # noqa: PLW0603
    if _cron_service is None:
        _cron_service = CronService(runner)
        try:
            # Only start if there's a running event loop
            asyncio.get_running_loop()
            asyncio.create_task(_cron_service.start())
            logger.info("Cron service started")
        except RuntimeError:
            # No event loop yet - cron service will start on first async use
            logger.debug(
                "Cron service initialized, will start when loop is available"
            )


def _ensure_initialized() -> None:
    """Initialize both runner and a2a_app from a single factory call."""
    global _runner, _a2a_app
    if _runner is None or _a2a_app is None:
        _runner, _a2a_app = WyzvrdFactory.create_wyzvrd()
        # Start cron service for ADK web
        _start_cron_service(_runner)


def get_runner() -> Runner:
    """Lazy initialization of the runner."""
    _ensure_initialized()
    return _runner


def get_a2a_app() -> Starlette:
    """Lazy initialization of the A2A app."""
    _ensure_initialized()
    return _a2a_app


def get_root_agent() -> BaseAgent:
    """Lazy initialization of the root agent."""
    return get_runner().app.root_agent


def __getattr__(name: str):
    """Module-level lazy attribute access.

    Provides runner, a2a_app, and root_agent at module level
    without eager initialization. Required for ADK web interface.
    """
    if name == "runner":
        return get_runner()
    elif name == "a2a_app":
        return get_a2a_app()
    elif name == "root_agent":
        return get_root_agent()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
