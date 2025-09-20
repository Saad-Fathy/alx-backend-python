# Unittests and Integration Tests

This project implements comprehensive unit and integration tests for a GitHub API client and utility functions.

## Project Structure

### Files

- **client.py**: GitHub API client with org and repository management
- **utils.py**: Utility functions including nested map access, HTTP requests, and string manipulation
- **fixtures.py**: Test data and fixtures for integration testing
- **test_client.py**: Unit and integration tests for the GitHub client
- **test_utils.py**: Unit tests for utility functions
- **test_fixtures.py**: Integration tests using parameterized fixtures

### Testing Strategy

#### Unit Tests
- Test individual methods in isolation
- Mock external dependencies (HTTP requests, file I/O)
- Use parameterized testing for multiple input scenarios
- Verify edge cases and error conditions

#### Integration Tests
- Test end-to-end workflows
- Use real fixture data that mimics API responses
- Verify interactions between components
- Test with both valid and edge-case data

## Running Tests

Execute all tests:

```bash
python3 -m unittest discover . "*.py" -v