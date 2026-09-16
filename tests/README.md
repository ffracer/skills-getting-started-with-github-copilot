# Test Suite Documentation

This directory contains the complete test suite for the Mergington High School Activity Management API. Tests follow the **AAA (Arrange-Act-Assert) pattern** for clarity and consistency.

## Test Structure

### Files

- **`conftest.py`** — Shared test configuration and fixtures
  - `client` fixture: TestClient for making HTTP requests
  - `sample_email` fixture: Test email addresses
  - `sample_activities` fixture: Expected activity names
  - `preset_participants` fixture: Pre-enrolled participants

- **`test_endpoints.py`** — Integration tests for all API endpoints
  - `TestRootEndpoint` — GET / redirect tests
  - `TestGetActivities` — GET /activities tests
  - `TestSignup` — POST /activities/{activity}/signup tests
  - `TestUnregister` — DELETE /activities/{activity}/signup tests

- **`test_activities_model.py`** — Unit tests for data structures and logic
  - `TestActivityDataStructure` — Activity field validation
  - `TestParticipantManagement` — Participant add/remove logic
  - `TestActivityValidation` — Input validation and error cases
  - `TestActivityCounts` — Participant counting and state persistence

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_endpoints.py -v
```

### Run specific test class
```bash
pytest tests/test_endpoints.py::TestSignup -v
```

### Run specific test
```bash
pytest tests/test_endpoints.py::TestSignup::test_signup_success -v
```

### Run tests matching pattern
```bash
pytest -k "signup" -v
```

### Run with coverage report
```bash
pytest --cov=src --cov-report=html
```
(Requires `pytest-cov` — install with `pip install pytest-cov`)

## AAA Pattern Explanation

Every test follows the **Arrange-Act-Assert (AAA)** pattern:

1. **Arrange** — Set up test data, fixtures, and preconditions
2. **Act** — Execute the code being tested (make HTTP request, call function)
3. **Assert** — Verify expected outcomes (status codes, response data, state changes)

### Example: Integration Test

```python
def test_signup_success(self, client, sample_email):
    # Arrange: Valid activity name and new student email
    activity_name = "Chess Club"
    email = sample_email

    # Act: Make POST request to signup endpoint
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Verify response status and content
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
```

### Example: Unit Test

```python
def test_signup_increases_participant_count(self, client):
    # Arrange: Get initial participant count
    activity_name = "Chess Club"
    email = "participant@test.com"
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])

    # Act: Sign up a new student
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Verify count increased by 1
    assert signup_response.status_code == 200
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity_name]["participants"])
    assert final_count == initial_count + 1
```

## Test Coverage

### Endpoints Tested

| Endpoint | Tests | Coverage |
|----------|-------|----------|
| GET / | 2 | Redirect behavior, successful resolution |
| GET /activities | 3 | All activities returned, structure validation, preset data |
| POST /activities/{activity}/signup | 5 | Success, duplicate detection, invalid activity, multiple signups |
| DELETE /activities/{activity}/signup | 5 | Success, removal verification, not enrolled error, invalid activity, roundtrip |

### Test Categories

**Integration Tests** (test_endpoints.py):
- HTTP request/response handling
- API endpoint functionality
- Error responses and status codes
- End-to-end workflows (signup → unregister)

**Unit Tests** (test_activities_model.py):
- Data structure validation
- Participant count tracking
- State persistence
- Input validation
- Edge cases and error conditions

## Adding New Tests

To add a new test:

1. **Choose the right file**
   - Integration tests (HTTP endpoints) → `test_endpoints.py`
   - Logic/data tests → `test_activities_model.py`

2. **Follow the AAA pattern**
   ```python
   def test_your_test_name(self, client):
       # Arrange: Set up preconditions
       
       # Act: Execute the code
       
       # Assert: Verify results
   ```

3. **Use fixtures from conftest.py**
   - Add fixture names as parameters to your test function
   - Fixtures automatically initialize before each test

4. **Add docstring comments**
   - Clearly state what is being arranged, acted, and asserted
   - Include the reason/scenario being tested

## Dependencies

- `pytest` — Test framework
- `pytest-asyncio` — Async test support
- `fastapi` — Web framework (contains TestClient)
- `httpx` — HTTP client (used by TestClient)

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Test Configuration

See `pytest.ini` for pytest configuration:
- `pythonpath = .` — Allows importing from project root
- `testpaths = tests` — Only discover tests in the tests/ directory
- `python_files = test_*.py` — Test file naming pattern
- `python_classes = Test*` — Test class naming pattern
- `python_functions = test_*` — Test function naming pattern
