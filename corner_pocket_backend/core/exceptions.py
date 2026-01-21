"""Custom application exceptions."""


class CornerPocketError(Exception):
    """Base exception for domain-specific errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
