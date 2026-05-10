"""Compendium management agent for maintaining the internal knowledge base."""

import pathlib

from google.adk.agents.llm_agent import LlmAgent
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.skills import load_skill_from_dir
from google.adk.tools.agent_tool import AgentTool

from agents.routing import ActiveSkillToolset
from agents.utils import get_model


def create_compendium_mgmt_agent() -> LlmAgent:
    """Create and return the compendium management agent.

    Returns:
        LlmAgent: Configured compendium management agent with
            web research capabilities.
    """
    from agents.sub_agents.web_research_agent import create_web_research_agent  # noqa: PLC0415, I001

    web_search_agent = create_web_research_agent()
    agent_tools = [
        AgentTool(agent=web_search_agent),
    ]
    function_tools = []
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
        name="compendium_mgmt_agent",
        model=get_model("compendium"),
        description=(
            "An expert knowledge base maintainer. Maintains the internal "
            "knowledge base called 'compendium'."
        ),
        instruction=(
            "You are the compendium management agent. Use `load_skill` to load "
            "the compendium skill. Once loaded, follow the skill's "
            "instructions to manage the compendium based on the user's request."
        ),
        tools=[
            skillset,
        ],
    )
