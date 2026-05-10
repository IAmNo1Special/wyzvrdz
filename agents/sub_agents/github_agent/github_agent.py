"""Github Agent - Github interaction capabilities."""

import os
import pathlib

from google.adk.agents import LlmAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.skills import load_skill_from_dir
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

from agents.routing import ActiveSkillToolset
from agents.utils import get_model


def create_github_agent():
    """Create an agent to interact with Github using Github's mcp server.

    Returns:
        LlmAgent: Configured github agent
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
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
                    "X-MCP-Toolsets": "all",
                    "X-MCP-Readonly": "true",
                },
            ),
        ),
    ]

    all_tools = skillsets + mcp_tools

    return LlmAgent(
        name="github_agent",
        model=get_model("github"),
        description=("Uses the Github mcp toolset to interact with Github."),
        instruction=(
            "You are a github specialist. Use the github mcp toolset to answer "
            "questions, and/or complete tasks related to Github."
        ),
        tools=all_tools,
    )
