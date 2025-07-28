"""
Login module for demonstration purposes.

Defines a simple `login` function that instantiates a `User`. There is a
deliberate circular import with `user.py` for demonstration of the AI
Debugging Copilot's capabilities.
"""

from .user import User  # This import contributes to the circular dependency


def login(username: str) -> User:
    """Authenticate a user and return a User instance."""
    return User(username)