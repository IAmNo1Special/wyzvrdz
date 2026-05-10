"""Main entry point for the Wyzvrdz application."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from discord_gateway.main import entrypoint

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")

if __name__ == "__main__":
    asyncio.run(entrypoint())
