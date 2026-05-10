"""Tool for active skill discovery via model-driven requests."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

if TYPE_CHECKING:
    from google.adk.tools.skill_toolset import SkillToolset

    from .skill_router import SkillRouter

logger = logging.getLogger(__name__)

MAX_SKILL_DISCOVERY_ATTEMPTS = 5


class RequestSkillTool(BaseTool):
    """Tool that allows the model to request skills via semantic matching.

    Replaces the catalog-based ListSkillsTool with an active discovery mechanism
    where the model identifies its own capability gaps and requests appropriate
    skills dynamically.
    """

    def __init__(self, router: SkillRouter, toolset: SkillToolset):
        """Initialize the RequestSkillTool.

        Args:
            router: The skill router for matching requests.
            toolset: The skill toolset for accessing skills.
        """
        super().__init__(
            name="request_skill",
            description=(
                "Discover skills by describing domain and capability. "
                "Returns up to 3 matching skills with metadata. "
                "Use this when you identify a gap in your capabilities. "
                "Use load_skill with the skill_name to load full instructions."
            ),
        )
        self._router = router
        self._toolset = toolset

    def _get_declaration(self) -> types.FunctionDeclaration | None:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": (
                            "The operational domain you need help with. "
                            "Examples: 'discord', 'filesystem', 'web research'."
                        ),
                    },
                    "capability": {
                        "type": "string",
                        "description": (
                            "The specific capability you need to perform. "
                            "Examples: 'send message', 'read files', "
                            "'fetch weather', 'search web'."
                        ),
                    },
                },
                "required": [],  # At least one required at runtime
            },
        )

    async def run_async(
        self, *, args: dict[str, Any], tool_context: ToolContext
    ) -> Any:
        """Route a skill request and activate the matching skill."""
        domain = args.get("domain", "").strip()
        capability = args.get("capability", "").strip()

        # Track attempt count - max 5 attempts per conversation
        agent_name = tool_context.agent_name
        state_key = f"_request_skill_attempts_{agent_name}"
        attempts = tool_context.state.get(state_key, 0)

        if attempts >= MAX_SKILL_DISCOVERY_ATTEMPTS:
            return {
                "error": (
                    "Maximum skill discovery attempts reached (5). "
                    "Assume the required skill does not exist and either: "
                    "1) Use available tools directly, or 2) Inform the user "
                    "that this capability is not available."
                ),
                "error_code": "MAX_ATTEMPTS_REACHED",
                "attempts": attempts,
            }

        # Increment attempt counter
        tool_context.state[state_key] = attempts + 1

        # Validate: at least one must be provided
        if not domain and not capability:
            return {
                "error": (
                    "Provide at least one of 'domain' or 'capability'. "
                    "Describe what area you need help with."
                ),
                "error_code": "INVALID_ARGUMENTS",
            }

        # Use whichever is provided for routing
        # If only one provided, use it for both stages
        domain_for_routing = domain or capability
        capability_for_routing = capability or domain

        # Route to top-K matching skills
        matches = await self._router.route(
            domain=domain_for_routing,
            capability=capability_for_routing,
            threshold=0.6,
            top_k=3,
        )

        if not matches:
            return {
                "error": (
                    "No matching skill found. "
                    f"Attempt {attempts + 1} of "
                    f"{MAX_SKILL_DISCOVERY_ATTEMPTS}. "
                    "Try describing your need differently."
                ),
                "error_code": "SKILL_NOT_FOUND",
                "requested_domain": domain or capability,
                "requested_capability": capability or domain,
                "attempts": attempts + 1,
                "max_attempts": MAX_SKILL_DISCOVERY_ATTEMPTS,
            }

        # Build matches list with frontmatter
        matches_data = []
        for skill_name, score in matches:
            skill = self._toolset._get_skill(skill_name)
            if skill:
                matches_data.append(
                    {
                        "skill_name": skill_name,
                        "score": round(score, 3),
                        "frontmatter": skill.frontmatter.model_dump(),
                    }
                )

        logger.debug(
            f"request_skill: '{domain}' + '{capability}' -> "
            f"{len(matches_data)} matches: "
            f"{[m['skill_name'] for m in matches_data]}"
        )

        # Reset attempt counter on successful discovery
        tool_context.state[state_key] = 0

        return {
            "matches": matches_data,
            "message": (
                f"Found {len(matches_data)} matching skill(s). "
                f"Use load_skill with the skill_name to load full instructions."
            ),
        }
