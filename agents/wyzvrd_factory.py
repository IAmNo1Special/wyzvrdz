"""A factory for creating Wyzvrdz."""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk import Runner
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.apps import App, ResumabilityConfig
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.code_executors import UnsafeLocalCodeExecutor
from google.adk.skills import load_skill_from_dir
from google.adk.tools import AgentTool, FunctionTool
from starlette.applications import Starlette

# from ag_ui_adk import AGUIToolset
from .configs import WYZVRD_SETTINGS
from .routing import ActiveSkillToolset
from .services import artifact_service, session_service
from .sub_agents import (
    create_compendium_mgmt_agent,
    create_discord_mgmt_agent,
    create_web_research_agent,
)
from .tools import generate_images
from .utils import get_model

logger = logging.getLogger(__name__)


class WyzvrdFactory:
    """Factory for creating configured Wyzard instances."""

    _MODEL = get_model("root")

    @staticmethod
    def create_wyzvrd(
        name: str = WYZVRD_SETTINGS.name,
    ) -> tuple[Runner, Starlette]:
        """Create a Wyzvrd.

        Args:
          name: Name to use for the Wyzvrd (default: my-wyzvrd)

        Returns:
          A tuple containing the Runner, App, LlmAgent,
          and A2A compatible Starlette App
        """
        # The web research agent must be created before
        #  the discord and compendium agents
        web_research_agent = create_web_research_agent()
        discord_mgmt_agent = create_discord_mgmt_agent()
        compendium_mgmt_agent = create_compendium_mgmt_agent()
        agent_tools = [
            AgentTool(agent=web_research_agent),
            AgentTool(agent=discord_mgmt_agent),
            AgentTool(agent=compendium_mgmt_agent),
        ]

        function_tools = [
            FunctionTool(generate_images, require_confirmation=True),
            # FunctionTool(save_as_skill),
            # PreloadMemoryTool(),
            # AGUIToolset()
        ]

        # Combine all tools used in skills
        skill_tools = agent_tools + function_tools
        skills_dir = Path(__file__).parent / "skills"
        skills = [load_skill_from_dir(skill) for skill in skills_dir.iterdir()]
        skillsets = [
            ActiveSkillToolset(
                skills=skills,
                additional_tools=skill_tools,
                code_executor=UnsafeLocalCodeExecutor(),
            )
        ]

        mcp_tools = []

        all_tools = skillsets + mcp_tools

        agent = LlmAgent(
            name=name,
            description=(
                "An intuitive, intelligent and adaptable Wyzvrd."
                " Prioritizes truth-seeking, truth-telling, and the pursuit of"
                " knowledge above all else."
            ),
            instruction=(
                "The first thing you need to do before proceeding with and/or "
                "responding to any user request is load your 'soul' skill. "
                "Use 'load_skill' with skill_name='soul' to load your core "
                "identity, behavior and capabilities."
            ),
            model=WyzvrdFactory._MODEL,
            tools=all_tools,
        )

        app = App(
            name=name,
            root_agent=agent,
            events_compaction_config=EventsCompactionConfig(
                compaction_interval=100,
                overlap_size=20,
                summarizer=LlmEventSummarizer(llm=get_model("summarizer")),
            ),
            resumability_config=ResumabilityConfig(
                is_resumable=True,
            ),
        )

        runner = Runner(
            app=app,
            # memory_service=memory_service,
            session_service=session_service,
            artifact_service=artifact_service,
        )

        # Make your agent A2A-compatible
        a2a_app = to_a2a(
            agent,
            host=WYZVRD_SETTINGS.a2a.host,
            port=WYZVRD_SETTINGS.a2a.port,
            runner=runner,
        )

        return runner, a2a_app


if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly.")
