"""Agentphone MCP Agent."""

import os
import pathlib

from google.adk.agents import LlmAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from agents.routing import ActiveSkillToolset
from agents.utils import get_model


def create_agentphone_agent():
    """Create an agent to interact with AgentPhone using AgentPhone MCP server.

    Returns:
        LlmAgent: Configured AgentPhone agent
    """
    agent_tools = []
    function_tools = []

    skill_tools = agent_tools + function_tools

    # Load the unified github skill
    skills_dir = pathlib.Path(__file__).parent / "skills"
    skills = [
        load_skill_from_dir(skill)
        for skill in skills_dir.iterdir()
        if skill.is_dir()
    ]

    # Toolset combining the unified skill with ADK tools
    skillsets = [
        ActiveSkillToolset(
            skills=skills,
            additional_tools=skill_tools,
            code_executor=UnsafeLocalCodeExecutor(),
        )
    ]

    mcp_tools = [
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "agentphone-mcp",
                    ],
                    env={
                        "AGENTPHONE_API_KEY": os.getenv("AGENTPHONE_API_KEY"),
                    },
                ),
                timeout=30,
            ),
        ),
    ]

    all_tools = skillsets + mcp_tools

    return LlmAgent(
        name="agentphone_agent",
        model=get_model("agentphone"),
        description=(
            "Uses the AgentPhone mcp toolset to interact with make phone "
            "calls, send SMS messages, and more by connecting to the "
            "AgentPhone service thru its mcp server."
        ),
        instruction=(
            "You are an AgentPhone specialist. Use the AgentPhone mcp "
            "toolset to answer questions, and/or complete tasks using the "
            "capabilities of AgentPhone."
        ),
        tools=all_tools,
    )
