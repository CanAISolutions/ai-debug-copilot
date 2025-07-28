"""
Tests for the demo login functionality.

These tests intentionally trigger a circular import error by importing
`src.auth.login`. The AI Debugging Copilot should detect the circular
import and propose a fix that removes the problematic import in
`user.py`.
"""

import unittest


class LoginTestCase(unittest.TestCase):
    """Tests for the login functionality."""

    def test_login_creates_user(self):
        """Test that login returns a user with the correct greeting."""
        # Import within the test to trigger the circular import error
        from src.auth.login import login  # type: ignore
        user = login('Alice')
        self.assertEqual(user.greet(), 'Hello, Alice')


if __name__ == '__main__':
    unittest.main()