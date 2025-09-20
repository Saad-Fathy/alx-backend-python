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

    @patch('client.get_json')
    @patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock)
    def test_public_repos(self) -> None:
        """
        Test that public_repos returns expected repository list and calls mocks once
        """
        # Get the mock objects (automatically injected by patch decorators)
        mock_public_repos_url = self._public_repos_url
        mock_get_json = self.get_json

        # Configure mocks with known values
        mock_public_repos_url.return_value = "https://api.github.com/repos"
        mock_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},  # No license
        ]
        mock_get_json.return_value = mock_repos_payload

        # Create client instance
        client = GithubOrgClient("test_org")

        # Test the public_repos method
        result = client.public_repos()

        # Verify the result contains only repos with licenses
        expected_repos = ["repo1", "repo2"]
        self.assertEqual(result, expected_repos)

        # Verify mocks were called exactly once
        mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with(mock_public_repos_url.return_value)