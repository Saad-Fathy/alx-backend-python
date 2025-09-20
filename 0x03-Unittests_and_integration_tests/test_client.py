#!/usr/bin/env python3
"""Unit tests for the GitHub API client."""

import unittest
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient unit tests."""

    @patch.object(GithubOrgClient, "org", new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org: PropertyMock) -> None:
        """
        Test that _public_repos_url returns the expected repos_url from org payload
        """
        # Configure mock to return known payload with repos_url
        known_payload = {"repos_url": "https://api.github.com/orgs/test_org/repos"}
        mock_org.return_value = known_payload

        # Create client instance
        client = GithubOrgClient("test_org")

        # Test the _public_repos_url property
        result = client._public_repos_url

        # Verify the result matches the expected repos_url
        self.assertEqual(result, known_payload["repos_url"])