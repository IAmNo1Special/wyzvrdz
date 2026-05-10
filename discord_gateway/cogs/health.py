"""Health cog: periodic heartbeat logging and bot uptime tracking."""

import asyncio
import time

from discord.ext import commands

from discord_gateway.cogs.shared import logger, spawn_background_task

# Heartbeat interval in seconds
_HEARTBEAT_INTERVAL = 300  # 5 minutes


class HealthCog(commands.Cog):
    """Monitors bot health and logs periodic heartbeats."""

    def __init__(self, bot: commands.Bot):
        """Initialize the HealthCog.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot
        self._start_time: float = 0.0
        self._heartbeat_task = None

    @commands.Cog.listener()
    async def on_ready(self):
        """Start heartbeat loop when the bot is ready."""
        self._start_time = time.monotonic()
        if self._heartbeat_task is None:
            self._heartbeat_task = spawn_background_task(
                self._heartbeat_loop(), name="health_heartbeat"
            )

    async def _heartbeat_loop(self):
        """Periodically log bot health status."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            uptime_secs = int(time.monotonic() - self._start_time)
            hours, remainder = divmod(uptime_secs, 3600)
            minutes, seconds = divmod(remainder, 60)
            latency = round(self.bot.latency * 1000)

            logger.info(
                "Heartbeat: uptime=%dh%dm%ds, guilds=%d, latency=%dms",
                hours,
                minutes,
                seconds,
                len(self.bot.guilds),
                latency,
            )
            await self._sleep(_HEARTBEAT_INTERVAL)

    async def _sleep(self, seconds: float):
        """Sleep that respects bot shutdown.

        Args:
            seconds: Duration to sleep in seconds.
        """
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            pass

    def cog_unload(self):
        """Cancel the heartbeat task when the cog is unloaded."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()


async def setup(bot: commands.Bot):
    """Set up the HealthCog.

    Args:
        bot: The Discord bot instance.
    """
    try:
        await bot.add_cog(HealthCog(bot))
    except Exception as e:
        print(f'ERROR in HealthCog "setup" function: {e}')
