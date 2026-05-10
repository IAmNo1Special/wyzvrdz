"""Sub-agent package for specialized agent implementations."""

from __future__ import annotations

from .compendium_mgmt_agent import create_compendium_mgmt_agent
from .discord_mgmt_agent import create_discord_mgmt_agent
from .web_research_agent import create_web_research_agent

__all__ = [
    "create_discord_mgmt_agent",
    "create_web_research_agent",
    "create_compendium_mgmt_agent",
]
