#!/usr/bin/env python3
"""
Unit tests for utility functions in utils.py
"""

import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


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
    def test_get_json(self, test_url: str, test_payload: dict, 
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


class TestMemoize(unittest.TestCase):
    """
    Test class for the memoize decorator
    """

    def test_memoize(self) -> None:
        """
        Test that memoize decorator caches results and only calls underlying method once
        """
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Patch the a_method to track calls
        with patch.object(TestClass, 'a_method') as mock_a_method:
            mock_a_method.return_value = 42
            
            # Create test instance
            test_instance = TestClass()
            
            # First call - should call a_method once
            result1 = test_instance.a_property()
            self.assertEqual(result1, 42)
            mock_a_method.assert_called_once()
            
            # Reset the call count for second test
            mock_a_method.reset_mock()
            
            # Second call - should return cached result, not call a_method
            result2 = test_instance.a_property()
            self.assertEqual(result2, 42)
            mock_a_method.assert_not_called()