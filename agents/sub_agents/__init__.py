"""Sub-agent package for specialized agent implementations."""

from __future__ import annotations

from .agentmail_agent import create_agentmail_agent
from .agentphone_agent import create_agentphone_agent
from .compendium_mgmt_agent import create_compendium_mgmt_agent
from .discord_mgmt_agent import create_discord_mgmt_agent
from .github_agent import create_github_agent

__all__ = [
    "create_agentmail_agent",
    "create_agentphone_agent",
    "create_compendium_mgmt_agent",
    "create_discord_mgmt_agent",
    "create_github_agent",
]
