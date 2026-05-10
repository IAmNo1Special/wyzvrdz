"""Discord Specialist Agent for Project Zion.

This module defines a specialized agent for Discord interactions,
providing a clean interface for the root agent to delegate tasks.
"""

from __future__ import annotations

import pathlib

from google.adk.agents import LlmAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.skills import load_skill_from_dir
from google.adk.tools import AgentTool, FunctionTool

from agents.routing import ActiveSkillToolset
from agents.utils import get_model

from .tools import (
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


def create_discord_mgmt_agent():
    """Create and configure the Discord management agent.

    Returns:
        The configured LlmAgent instance.
    """
    from .. import create_web_research_agent  # noqa: PLC0415

    web_research_agent = create_web_research_agent()
    agent_tools = [
        AgentTool(agent=web_research_agent),
    ]
    function_tools = [
        FunctionTool(add_reaction),
        FunctionTool(send_message),
        FunctionTool(send_embed),
        FunctionTool(send_message_with_components),
        FunctionTool(send_modal_button),
        FunctionTool(create_thread),
        FunctionTool(get_channel_messages),
        FunctionTool(get_message),
        FunctionTool(edit_message),
        FunctionTool(delete_message),
        FunctionTool(get_guild_channels),
        FunctionTool(get_guild_members),
        FunctionTool(get_guild_roles),
        FunctionTool(update_nickname),
        FunctionTool(update_username),
        FunctionTool(get_user),
    ]
    all_additional_tools = function_tools + agent_tools

    skills_dir = pathlib.Path(__file__).parent / "skills"
    skills = [load_skill_from_dir(skill) for skill in skills_dir.iterdir()]

    # Toolset using the script-based patterns
    skillset = ActiveSkillToolset(
        skills=skills,
        additional_tools=all_additional_tools,
        code_executor=UnsafeLocalCodeExecutor(),
    )

    return LlmAgent(
        name="discord_mgmt_agent",
        model=get_model("discord"),
        description=(
            "An expert in Discord actions including messaging, "
            "reactions, channel management, and server info."
        ),
        instruction=(
            "First, read the 'discord' skill. "
            "Use the 'discord' skill to interact on behalf of the user."
        ),
        tools=[skillset],
    )
