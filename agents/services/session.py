"""Session service for the agents package."""

import os

from google.adk.sessions import DatabaseSessionService


def _get_db_path() -> str:
    """Get the database path from env var or default to data/session.db."""
    # Allow Docker to mount a specific data directory
    data_dir = os.getenv("WYZVRDZ_DATA_DIR")
    if data_dir:
        return os.path.join(data_dir, "session.db")

    # Default: project root / data/
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    data_path = os.path.join(project_root, "data")
    os.makedirs(data_path, exist_ok=True)
    return os.path.join(data_path, "session.db")


class SessionService(DatabaseSessionService):
    """Custom session service with SQLite backend."""

    def __init__(self):
        """Initialize the session service with SQLite database."""
        db_path = _get_db_path()
        db_url = f"sqlite+aiosqlite:///{db_path.replace(os.sep, '/')}"  # noqa: E501
        super().__init__(db_url=db_url)


session_service = SessionService()
