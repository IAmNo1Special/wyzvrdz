"""Core cog: on_ready event, background task spawning, and bot lifecycle."""

from discord.ext import commands
from google.genai import types

from agents.agent import runner
from agents.configs import WYZVRD_SETTINGS
from discord_gateway.cogs.shared import logger, spawn_background_task
from discord_gateway.scripts.watcher import main as run_watcher

USER_ID = WYZVRD_SETTINGS.user_id

# Number of recent DM messages to inject into the ADK session on startup
_CONTEXT_INJECTION_LIMIT = 20


class CoreCog(commands.Cog):
    """Handles bot lifecycle events and background tasks."""

    def __init__(self, bot: commands.Bot):
        """Initialize the CoreCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Event handler called when the bot is connected and ready."""
        logger.info("--- Discord Bot Online ---")
        logger.info(
            f"Logged in as: {self.bot.user.name} (ID: {self.bot.user.id})"
        )

        logger.info("Syncing slash commands...")
        try:
            synced = await self.bot.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")

        # Inject recent DM history into the ADK session for context continuity
        await self._inject_recent_context()

        logger.info("--------------------------")
        spawn_background_task(run_watcher(logger=logger), name="watcher")

    async def _inject_recent_context(self):
        """Fetch recent DM history and inject it into the ADK session.

        This ensures the agent has conversation context after a bot restart,
        so it doesn't lose track of ongoing discussions.
        """
        session_id = f"discord_{USER_ID}"

        try:
            # Ensure the session exists
            session_obj = await runner.session_service.get_session(
                app_name=WYZVRD_SETTINGS.name,
                user_id=USER_ID,
                session_id=session_id,
            )
            if not session_obj:
                await runner.session_service.create_session(
                    app_name=WYZVRD_SETTINGS.name,
                    user_id=USER_ID,
                    session_id=session_id,
                    state={},
                )

            # Find the user's DM channel
            # Extract numeric ID from formatted USER_ID
            # (e.g., "user-1234567890")
            user_id_str = (
                USER_ID.split("-")[-1] if "-" in str(USER_ID) else str(USER_ID)
            )
            user = self.bot.get_user(int(user_id_str))
            if not user:
                logger.info("Context injection: user not cached, skipping.")
                return

            dm_channel = user.dm_channel
            if not dm_channel:
                dm_channel = await user.create_dm()

            # Fetch recent messages (newest first)
            messages = await dm_channel.history(
                limit=_CONTEXT_INJECTION_LIMIT
            ).flatten()
            if not messages:
                logger.info("Context injection: no DM history found.")
                return

            # Reverse to chronological order and build context
            messages.reverse()
            context_lines = []
            for msg in messages:
                if msg.author == self.bot.user:
                    context_lines.append(f"Bot: {msg.content}")
                else:
                    context_lines.append(f"User: {msg.content}")

            context_text = "\n".join(context_lines)
            if not context_text.strip():
                return

            # Inject as a system note into the session
            context_content = types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=(
                            "[System Note: Conversation context restored after "
                            f"bot restart. Recent DM history:\n{context_text}]"
                        )
                    )
                ],
            )

            await runner.run_async(
                user_id=USER_ID,
                session_id=session_id,
                new_message=context_content,
            )
            logger.info(
                "Context injection: restored %d messages from DM history.",
                len(messages),
            )
        except Exception as e:
            # Non-fatal: context injection is best-effort
            logger.warning("Context injection failed (non-fatal): %s", e)


async def setup(bot: commands.Bot):
    """Set up the CoreCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        await bot.add_cog(CoreCog(bot))
    except Exception as e:
        print(f'ERROR in CoreCog "setup" function: {e}')
