"""Skill management tools for the agents package."""

import logging

from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


async def save_as_skill(ctx: ToolContext) -> dict[str, str | dict]:
    """Triggers distillation of current session into a procedural skill.

    Call this when a complex task is completed successfully and should be
    remembered as a 'how-to'.

    Returns:
        dict with status, message, and optional data.
    """
    logger.debug("Saving session as skill...")
    try:
        # Set flag to trigger distillation in after_run_callback
        ctx.state["distill_session"] = True
    except Exception as e:
        logger.exception("Failed to save session as skill")
        return {
            "status": "error",
            "message": f"Error marking session for distillation: {str(e)}",
            "data": {
                "user_id": ctx.user_id,
                "session_id": ctx.session.id,
                "invocation_id": ctx.invocation_id,
            },
        }
    else:
        logger.debug("Session saved as skill")
        return {
            "status": "success",
            "message": (
                "Session marked for distillation into a skill. "
                "This will happen at the end of this turn."
            ),
            "data": {
                "user_id": ctx.user_id,
                "session_id": ctx.session.id,
                "invocation_id": ctx.invocation_id,
            },
        }
