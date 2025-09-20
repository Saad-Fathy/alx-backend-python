#!/usr/bin/env python3
"""Unit tests for the GitHub API client."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient."""

    @patch.object(GithubOrgClient, "org", new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org) -> None:
        """Test that _public_repos_url returns the expected repos_url from org
        payload.
        """
        known_payload = {"repos_url": "http://test/repos"}
        mock_org.return_value = known_payload

        client = GithubOrgClient("test_org")
        result = client._public_repos_url

        self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    @patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock)
    def test_public_repos(self) -> None:
        """Test that public_repos returns expected repository list."""
        mock_public_repos_url = self._public_repos_url
        mock_get_json = self.get_json

        mock_public_repos_url.return_value = "http://test/repos"
        mock_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = mock_repos_payload

        client = GithubOrgClient("test_org")
        result = client.public_repos()

        expected_repos = ["repo1", "repo2"]
        self.assertEqual(result, expected_repos)

        mock_public_repos_url.assert_called_once()
        mock_get_json.assert_called_once_with(mock_public_repos_url.return_value)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected) -> None:
        """Test that has_license returns expected result for given repository
        and license key.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient using fixtures."""

    @classmethod
    def setUpClass(cls):
        """Set up the mock for requests.get with fixture data."""
        cls.get_patcher = patch('utils.requests.get')
        cls.mock_requests = cls.get_patcher.start()
        cls.mock_requests.return_value.json.side_effect = [
            cls.org_payload,
            cls.repos_payload,
        ]

    def test_public_repos(self):
        """Test GithubOrgClient.public_repos returns expected results based on
        fixtures.
        """
        test_client = GithubOrgClient("google")
        repos = test_client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test GithubOrgClient.public_repos with apache-2.0 license filter."""
        test_client = GithubOrgClient("google")
        repos = test_client.public_repos("apache-2.0")
        self.assertEqual(repos, self.apache2_repos)

    @classmethod
    def tearDownClass(cls):
        """Clean up by stopping the patcher."""
        cls.get_patcher.stop()


if __name__ == "__main__":
    unittest.main()
