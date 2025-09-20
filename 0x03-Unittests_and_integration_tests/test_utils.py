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
    def test_access_nested_map(
        self,
        nested_map: dict,
        path: tuple,
        expected: any,
    ) -> None:
        """
        Test that access_nested_map returns the expected result for given inputs
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: dict,
        path: tuple,
        expected_message: str,
    ) -> None:
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
    def test_get_json(
        self,
        test_url: str,
        test_payload: dict,
        mock_requests: MagicMock,
    ) -> None:
        """
        Test that get_json returns expected result and mocks HTTP call correctly
        """
        mock_requests.return_value.json.return_value = test_payload

        result = get_json(test_url)

        self.assertEqual(result, test_payload)
        mock_requests.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """
    Test class for the memoize decorator
    """

    def test_memoize(self) -> None:
        """
        Test that memoize decorator caches results and only calls underlying
        method once
        """
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_instance = TestClass()

        mock_a_method = patch.object(test_instance, 'a_method')
        mock_a_method_instance = mock_a_method.start()
        mock_a_method_instance.return_value = 42

        try:
            result1 = test_instance.a_property()
            self.assertEqual(result1, 42)
            mock_a_method_instance.assert_called_once()

            mock_a_method_instance.reset_mock()

            result2 = test_instance.a_property()
            self.assertEqual(result2, 42)
            mock_a_method_instance.assert_not_called()
        finally:
            mock_a_method.stop()