"""Discord Channel Adapter.

This standalone script connects the ADK runner and agent to Discord as a bot.
It handles message routing, rich interactions, and native slash commands.
"""

import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from pathlib import Path
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from agents.configs import ROOT_DIR
from discord_gateway.state import init_state

load_dotenv()

# Configure logging for background process
logger = logging.getLogger("discord_bot")

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def load_cogs():
    """Discover and load all cogs from the cogs directory."""
    cogs_dir = Path(__file__).parent / "cogs"

    # Load flat .py files directly in cogs/
    # Skip 'shared.py' as it's a utility module, not a cog
    _skip_files = {"shared"}
    for filepath in cogs_dir.iterdir():
        if (
            filepath.is_file()
            and filepath.suffix == ".py"
            and not filepath.name.startswith("_")
            and filepath.stem not in _skip_files
        ):
            ext = f"discord_gateway.cogs.{filepath.stem}"
            try:
                await bot.load_extension(ext)
                logger.info(f"Loaded cog: {ext}")
            except Exception as e:
                logger.error(f"Failed to load cog {ext}: {e}")

    # Load nested cogs from subdirectories
    for cog_dir in cogs_dir.iterdir():
        if cog_dir.is_dir() and not cog_dir.name.startswith("_"):
            for filename in cog_dir.iterdir():
                if filename.suffix == ".py" and not filename.name.startswith(
                    "_"
                ):
                    ext = f"discord_gateway.cogs.{cog_dir.name}.{filename.stem}"
                    try:
                        await bot.load_extension(ext)
                        logger.info(f"Loaded cog: {ext}")
                    except Exception as e:
                        logger.error(f"Failed to load cog {ext}: {e}")


def setup_logging():
    """Configure logging to file for background process execution."""
    log_path = Path(ROOT_DIR) / "logs" / "discord_bot.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                log_path,
                maxBytes=10_000_000,
                backupCount=3,
                encoding="utf-8",
            ),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_path


async def entrypoint():
    """Main entry point for running the Discord bot as a background process."""
    log_path = setup_logging()
    logger.info("Discord Bot starting, logs: %s", log_path)

    # Initialize global state
    state = init_state()

    await load_cogs()

    discord_bot_token = getenv("DISCORD_BOT_TOKEN", "")
    if not discord_bot_token:
        logger.error("DISCORD_BOT_TOKEN not found. Exiting.")
        sys.exit(1)

    try:
        async with bot:
            await bot.start(discord_bot_token)
    except Exception as e:
        logger.exception("Bot crashed: %s", e)
        sys.exit(1)
    finally:
        # Cleanup state and sessions
        await state.shutdown()
        logger.info("Discord Bot shutdown complete.")
