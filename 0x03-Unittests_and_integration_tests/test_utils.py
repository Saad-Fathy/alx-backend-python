#!/usr/bin/env python3
"""
Unit tests for utility functions in utils.py
"""

import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from utils import access_nested_map, get_json


class TestAccessNestedMap(unittest.TestCase):
    """
    Test class for the access_nested_map utility function
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: dict, path: tuple, expected: any) -> None:
        """
        Test that access_nested_map returns the expected result for given inputs
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(self, nested_map: dict, path: tuple, 
                                       expected_message: str) -> None:
        """
        Test that access_nested_map raises KeyError with expected message
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), expected_message)


class TestGetJson(unittest.TestCase):
    """
    Test class for the get_json utility function
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get(self, test_url: str, test_payload: dict, 
                 mock_requests: MagicMock) -> None:
        """
        Test that get_json returns expected result and mocks HTTP call correctly
        """
        # Configure the mock to return the test payload when .json() is called
        mock_requests.return_value.json.return_value = test_payload
        
        # Call the function under test
        result = get_json(test_url)
        
        # Verify the result matches expected payload
        self.assertEqual(result, test_payload)
        
        # Verify the mock was called exactly once with the correct URL
        mock_requests.assert_called_once_with(test_url)