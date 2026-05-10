"""Cron service for scheduling and executing periodic jobs."""

import asyncio
import datetime
import json
import logging
from pathlib import Path
import random

from filelock import FileLock, Timeout
from google.genai.types import Content, Part

from ..configs import WYZVRD_SETTINGS

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
JOBS_FILE = BASE_DIR / "skills" / "cron-manager" / "assets" / "cron_jobs.json"
LOCK_FILE = JOBS_FILE.with_suffix(".lock")
HEARTBEAT_FILE = (
    BASE_DIR / "skills" / "cron-manager" / "assets" / "cron_service.heartbeat"
)
USER_ID = WYZVRD_SETTINGS.user_id


class WyzvrdCronJob:
    """Represents a cron job with scheduling configuration."""

    def __init__(self, **kwargs):
        """Initialize a cron job from keyword arguments."""
        # Unpack all keys from JSON
        self.name = kwargs.get("name")
        self.prompt = kwargs.get("prompt")
        self.fixed_date = kwargs.get("fixed_date")
        self.fixed_time = kwargs.get("fixed_time")
        self.interval_minutes = kwargs.get("interval_minutes")
        self.interval_hours = kwargs.get("interval_hours")
        self.interval_days = kwargs.get("interval_days")
        self.interval_weeks = kwargs.get("interval_weeks")
        self.interval_months = kwargs.get("interval_months")
        self.interval_years = kwargs.get("interval_years")
        self.is_random = kwargs.get("is_random", False)
        self.is_random_date = kwargs.get("is_random_date", False)
        self.random_target_time = kwargs.get("random_target_time")
        self.last_run = kwargs.get("last_run")

    def get_total_interval_seconds(self) -> float:
        """Calculates total seconds across all interval keys."""
        seconds = 0
        if self.interval_minutes:
            seconds += self.interval_minutes * 60
        if self.interval_hours:
            seconds += self.interval_hours * 3600
        if self.interval_days:
            seconds += self.interval_days * 86400
        if self.interval_weeks:
            seconds += self.interval_weeks * 604800
        if self.interval_months:
            seconds += self.interval_months * 2592000  # 30-day approx
        if self.interval_years:
            seconds += self.interval_years * 31536000
        return seconds

    def should_run(self) -> bool:
        """Check if the job should run based on schedule."""
        now = datetime.datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        now_time = now.strftime("%H:%M")

        # 1. Date Check (Strict match for fixed or random-target dates)
        if self.fixed_date and self.fixed_date != today_str:
            return False

        # 2. Random logic - compare dates using ISO format
        if self.is_random and self.random_target_time:
            last_run_date = self.last_run[:10] if self.last_run else None
            return (
                now_time == self.random_target_time
                and last_run_date != today_str
            )

        # 3. Fixed Time logic - compare times, checking we haven't run today
        if self.fixed_time:
            last_run_date = self.last_run[:10] if self.last_run else None
            return now_time == self.fixed_time and last_run_date != today_str

        # 4. Multi-Unit Interval logic
        total_sec = self.get_total_interval_seconds()
        if total_sec > 0:
            if not self.last_run:
                return True
            last_run_dt = datetime.datetime.fromisoformat(self.last_run)
            return (now - last_run_dt).total_seconds() >= total_sec

        return False

    def generate_next_run(self, force: bool = False):
        """Seeds the next random events.

        Args:
            force: If True, always generate new values even if they exist.
                   If False, only generate if values are not set.
        """
        if self.is_random and (force or not self.random_target_time):
            self.random_target_time = (
                f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
            )
        if self.is_random_date and (force or not self.fixed_date):
            days_out = random.randint(1, 30)
            self.fixed_date = (
                datetime.datetime.now() + datetime.timedelta(days=days_out)
            ).strftime("%Y-%m-%d")

    def to_dict(self):
        """Convert job to dictionary."""
        return self.__dict__


class CronService:
    """Service for managing and executing cron jobs."""

    def __init__(self, runner):
        """Initialize the cron service.

        Args:
            runner: The agent runner for executing jobs.
        """
        self.runner = runner
        self.jobs = self.load_jobs()
        self.active_now = []

    def load_jobs(self) -> list[WyzvrdCronJob]:
        """Load jobs with cross-process file locking."""
        lock = FileLock(LOCK_FILE, timeout=5)
        try:
            with lock:
                if not JOBS_FILE.exists():
                    return []
                with open(JOBS_FILE) as f:
                    data = json.load(f)
                    return [WyzvrdCronJob(**j) for j in data]
        except Timeout:
            logger.warning(
                "Could not acquire lock for loading jobs, returning cached jobs"
            )
            return self.jobs  # Return previously loaded jobs

    def save_jobs(self):
        """Atomic file write with cross-process locking."""
        lock = FileLock(LOCK_FILE, timeout=5)
        tmp_file = JOBS_FILE.with_suffix(".tmp")
        try:
            with lock:
                with open(tmp_file, "w") as f:
                    json.dump([j.to_dict() for j in self.jobs], f, indent=4)
                tmp_file.replace(JOBS_FILE)
        except Timeout:
            logger.warning(
                "Could not acquire lock for saving jobs, "
                "will retry on next cycle"
            )
        except Exception as e:
            logger.error(f"Failed to save jobs: {e}")
            if tmp_file.exists():
                tmp_file.unlink()

    async def run_task(self, job: WyzvrdCronJob):
        """Execute a single cron job."""
        logger.info(f" Executing Cron Job: {job.name}")
        lock_file = (
            BASE_DIR / "skills" / "cron-manager" / "assets" / f"{job.name}.lock"
        )
        lock_file.parent.mkdir(parents=True, exist_ok=True)

        # Mark as active
        self.active_now.append(job.name)
        # Write the start time to the lock
        lock_file.write_text(datetime.datetime.now().isoformat())

        session = None
        try:
            # Create a dedicated session for this cron job
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app.name,
                user_id=USER_ID,
                state={"type": "cron_job", "job_name": job.name},
            )
            logger.debug(f"Created session {session.id} for job '{job.name}'")

            # Iterate through the generator to ensure the agent completes
            content = Content(
                role="user", parts=[Part.from_text(text=job.prompt)]
            )
            async for event in self.runner.run_async(
                user_id=USER_ID, session_id=session.id, new_message=content
            ):
                if event.is_final_response():
                    response_text = (
                        event.content.parts[0].text
                        if event.content and event.content.parts
                        else ""
                    )
                    logger.info(
                        f"Cron Job '{job.name}' completed. "
                        f"Response: {response_text[:200]}..."
                    )
        except Exception as e:
            logger.error(f"Cron Job '{job.name}' failed: {e}", exc_info=True)
        finally:
            # Mark as inactive
            if job.name in self.active_now:
                self.active_now.remove(job.name)
            if lock_file.exists():
                lock_file.unlink()

    async def start(self):
        """Start the cron service loop."""
        logger.info(f"Cron service started - {len(self.jobs)} jobs loaded")
        while True:
            HEARTBEAT_FILE.write_text(datetime.datetime.now().isoformat())
            # 1. Load and Hydrate
            self.jobs = self.load_jobs()
            updated = False
            now = datetime.datetime.now()

            for job in self.jobs:
                # Catch empty random settings
                if (job.is_random and not job.random_target_time) or (
                    job.is_random_date and not job.fixed_date
                ):
                    job.generate_next_run()
                    updated = True

                # 2. Check Execution
                should_run = job.should_run()
                total_sec = job.get_total_interval_seconds()
                logger.debug(
                    f"Job '{job.name}': should_run={should_run}, "
                    f"last_run={job.last_run}, interval_sec={total_sec}"
                )

                if should_run:
                    logger.info(f"Job '{job.name}' triggered - executing now")
                    # Update State - always use ISO format for consistency
                    job.last_run = now.isoformat()

                    if job.is_random or job.is_random_date:
                        # Regenerate for next occurrence after successful run
                        job.generate_next_run(force=True)

                    updated = True
                    asyncio.create_task(self.run_task(job))

            if updated:
                self.save_jobs()

            await asyncio.sleep(20)


if __name__ == "__main__":
    raise SystemExit(
        "CronService must be instantiated with a runner. "
        "Import and use from the main application."
    )
