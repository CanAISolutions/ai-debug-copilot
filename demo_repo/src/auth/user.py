"""
User module for demonstration purposes.

This module intentionally contains a circular import to illustrate how the
AI Debugging Copilot can detect and fix such issues. The circular
dependency arises because this file imports the `login` function from
`login.py`, while `login.py` also imports `User` from this module.
"""

# Removed circular import


class User:
    def __init__(self, username: str):
        self.username = username

    def greet(self) -> str:
        """Return a greeting for the user."""
        return f"Hello, {self.username}"


def get_current_user() -> 'User':
    """Dummy function that demonstrates usage of login and circular imports."""
    # This call will trigger the circular import at runtime
    return login('demo')