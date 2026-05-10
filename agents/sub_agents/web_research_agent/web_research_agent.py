"""Web Research Agent - Combined search and URL context capabilities."""

import pathlib

from google.adk.agents import LlmAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.skills import load_skill_from_dir
from google.adk.tools import google_search, url_context
from google.adk.tools.agent_tool import AgentTool

from agents.routing import ActiveSkillToolset
from agents.utils import get_model


def create_web_research_agent():
    """Create a web research agent with search & URL analysis capabilities.

    Returns:
        LlmAgent: Configured web research agent
    """
    google_search_agent = LlmAgent(
        name="google_search_agent",
        model=get_model("google_search"),
        description=("Uses Google Search to research topics on the web."),
        instruction=(
            "You are a Google Search specialist. Use the 'google_search' tool "
            "to find information on the web."
        ),
        tools=[google_search],
    )

    url_context_agent = LlmAgent(
        name="url_context_agent",
        model=get_model("url_context"),
        description=("Uses URL analysis to research topics on the web."),
        instruction=(
            "You are a URL analysis specialist. Use the 'url_context' tool "
            "to analyze URLs and extract information."
        ),
        tools=[url_context],
    )

    agent_tools = [
        AgentTool(google_search_agent),
        AgentTool(url_context_agent),
    ]

    # Load the unified web-research skill
    skills_dir = pathlib.Path(__file__).parent / "skills"
    skills = [
        load_skill_from_dir(skill)
        for skill in skills_dir.iterdir()
        if skill.is_dir()
    ]

    # Toolset combining the unified skill with ADK tools
    skillset = ActiveSkillToolset(
        skills=skills,
        additional_tools=agent_tools,
        code_executor=UnsafeLocalCodeExecutor(),
    )

    return LlmAgent(
        name="web_research_agent",
        model=get_model("web_research"),
        description=(
            "Uses Google Search and URL analysis to research topics on the web."
        ),
        instruction=(
            "You are a web research specialist. Use the 'web-research' skill "
            "to determine how to best reply to the user's query."
        ),
        tools=[skillset],
    )
