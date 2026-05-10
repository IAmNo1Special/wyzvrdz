"""SkillToolset with active discovery replacing catalog-based browsing."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.code_executors.base_code_executor import BaseCodeExecutor
from google.adk.models.llm_request import LlmRequest
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.skill_toolset import (
    LoadSkillTool as BaseLoadSkillTool,
    SkillToolset,
)
from google.adk.tools.tool_context import ToolContext
from moss import MossClient

from .request_skill_tool import RequestSkillTool
from .skill_router import SkillRouter

if TYPE_CHECKING:
    from google.adk.agents.llm_agent import ToolUnion
    from google.adk.skills.models import Skill

logger = logging.getLogger(__name__)


class LoadSkillTool(BaseLoadSkillTool):
    """Wrapper around ADK LoadSkillTool with logging for metrics."""

    async def run_async(self, *, args: dict, tool_context: ToolContext) -> dict:
        """Load skill and log which one was loaded."""
        skill_name = args.get("name", "")
        logger.debug(f"load_skill: Loading skill '{skill_name}'")
        result = await super().run_async(args=args, tool_context=tool_context)
        logger.debug(f"load_skill: Successfully loaded '{skill_name}'")
        return result


class ActiveSkillToolset(SkillToolset):
    """A SkillToolset that uses active discovery instead of catalog browsing.

    Unlike the standard SkillToolset which injects a full XML catalog of all
    skills into every LLM request, this toolset:

    1. Removes the skill catalog from the system prompt
    2. Replaces ListSkillsTool with RequestSkillTool
    3. Instructs the model to use request_skill when needed
    4. Uses embedding-based semantic routing to match requests to skills

    This implements the "Full Active Discovery" pattern from MCP-Zero applied
    to the AgentSkills architecture. Benefits include:
    - Zero context tax (no skill catalog in every request)
    - Iterative skill chaining
    - State-dependent discovery
    - Better semantic alignment
    """

    _ACTIVE_DISCOVERY_INSTRUCTION = (
        "You have access to specialized skills that extend your capabilities. "
        "When you need domain expertise or capabilities beyond your knowledge, "
        "use the two-step discovery process:\n\n"
        "Step 1: Use `request_skill` to find a skill\n"
        "- Provide 'domain': the area you need help with\n"
        "- Provide 'capability': what specific action you need\n"
        "- Returns lightweight metadata (name + description) for preview\n\n"
        "Step 2: Use `load_skill` to load the full skill\n"
        "- Provide 'name': the skill name returned by request_skill\n"
        "- Returns full instructions, resources, and capabilities\n\n"
        "Once a skill is loaded:\n"
        "1. Read and follow its instructions exactly\n"
        "2. Use `load_skill_resource` to view skill files\n"
        "3. Use `run_skill_script` to execute scripts from the skill\n"
        "4. If you need another skill, call `request_skill` again\n\n"
        "Key principle: Only load skills when you actually need them. "
        "Don't preload skills - request them at the moment of need."
    )

    def __init__(  # noqa: PLR0913
        self,
        skills: list[Skill],
        *,
        code_executor: BaseCodeExecutor | None = None,
        script_timeout: int = 300,
        additional_tools: list[ToolUnion] | None = None,
        moss_client: MossClient | None = None,
    ):
        """Initialize ActiveSkillToolset.

        Args:
            skills: List of skills to register
            code_executor: Optional code executor for script execution
            script_timeout: Timeout in seconds for shell scripts (default 300)
            additional_tools: Tools available to skills via adk_additional_tools
            moss_client: Optional MossClient for semantic routing
        """
        super().__init__(
            skills=skills,
            code_executor=code_executor,
            script_timeout=script_timeout,
            additional_tools=additional_tools,
        )

        # Create router for semantic matching
        self._router = SkillRouter(
            skills=self._skills,
            client=moss_client,
        )
        self._router_initialized = False
        self._router_failed = False

    async def _ensure_router(self) -> None:
        """Initialize the router if not already done."""
        if not self._router_initialized and not self._router_failed:
            try:
                await self._router.initialize()
                self._router_initialized = True
            except Exception as e:
                logger.error(
                    f"Failed to initialize SkillRouter: {e}. "
                    "Falling back to standard catalog."
                )
                self._router_failed = True

    async def get_tools(
        self, readonly_context: ReadonlyContext | None = None
    ) -> list[BaseTool]:
        """Return tools with RequestSkillTool replacing ListSkillsTool.

        Keeps all other tools but swaps ListSkillsTool for RequestSkillTool.
        """
        await self._ensure_router()

        if self._router_failed:
            return await super().get_tools(readonly_context)

        # Get base tools from parent
        base_tools = [
            LoadSkillTool(self),
            LoadSkillResourceTool(self),
            RunSkillScriptTool(self),
            RequestSkillTool(router=self._router, toolset=self),
        ]

        # Resolve dynamic tools from skill activations (same as parent)
        dynamic_tools = await self._resolve_additional_tools_from_state(
            readonly_context
        )

        return base_tools + dynamic_tools

    async def process_llm_request(
        self,
        *,
        tool_context: ToolContext,
        llm_request: LlmRequest,
    ) -> None:
        """Inject minimal active discovery instruction instead of full catalog.

        This replaces the parent's behavior of injecting:
        - _DEFAULT_SKILL_SYSTEM_INSTRUCTION (behavioral guide)
        - XML catalog of all skills (can be 1000+ tokens)

        With a single focused instruction (~200 tokens).
        """
        await self._ensure_router()

        if self._router_failed:
            await super().process_llm_request(
                tool_context=tool_context, llm_request=llm_request
            )
            return

        llm_request.append_instructions([self._ACTIVE_DISCOVERY_INSTRUCTION])


from google.adk.tools.skill_toolset import (  # noqa: E402
    LoadSkillResourceTool,
    RunSkillScriptTool,
)
