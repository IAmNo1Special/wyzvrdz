"""Agentmail MCP Agent."""

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


def create_agentmail_agent():
    """Create an agent to interact with AgentMail using AgentMail MCP server.

    Returns:
        LlmAgent: Configured AgentMail agent
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
                        "agentmail-mcp",
                    ],
                    env={
                        "AGENTMAIL_API_KEY": os.getenv("AGENTMAIL_API_KEY"),
                    },
                ),
                timeout=30,
            ),
        )
    ]

    all_tools = skillsets + mcp_tools

    return LlmAgent(
        name="agentmail_agent",
        model=get_model("agentmail"),
        description=(
            "Uses the AgentMail mcp toolset to send/receive/manage emails, "
            "and more by connecting to the AgentMail service thru its "
            "mcp server."
        ),
        instruction=(
            "You are an AgentMail specialist. Use the AgentMail mcp "
            "toolset to answer questions about emails, and/or complete "
            "tasks related to the AgentMail service."
        ),
        tools=all_tools,
    )
