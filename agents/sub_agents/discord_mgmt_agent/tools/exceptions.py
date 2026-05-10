"""Discord API exceptions for structured error handling."""


class DiscordAPIError(Exception):
    """Base exception for Discord API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        """Initialize base exception."""
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(DiscordAPIError):
    """Raised when rate limit is exceeded after retries."""

    def __init__(
        self,
        retry_after: float,
        message: str = "Rate limit exceeded",
    ):
        """Initialize rate limit exception."""
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class PermissionError(DiscordAPIError):
    """Raised when the bot lacks required permissions."""

    def __init__(self, permission: str, message: str | None = None):
        """Initialize permission exception."""
        if message is None:
            message = f"Missing required permission: {permission}"
        super().__init__(message, status_code=403)
        self.permission = permission


class NotFoundError(DiscordAPIError):
    """Raised when a resource is not found (404)."""

    def __init__(self, resource: str, resource_id: str):
        """Initialize not found exception."""
        super().__init__(
            f"{resource} not found: {resource_id}",
            status_code=404,
        )
        self.resource = resource
        self.resource_id = resource_id


class ServerError(DiscordAPIError):
    """Raised when Discord returns a 5xx error after retries."""

    def __init__(self, status_code: int, message: str = "Discord server error"):
        """Initialize server error exception."""
        super().__init__(message, status_code=status_code)


class ValidationError(DiscordAPIError):
    """Raised when request validation fails (400)."""

    def __init__(self, message: str, errors: dict | None = None):
        """Initialize validation exception."""
        super().__init__(message, status_code=400)
        self.errors = errors or {}
