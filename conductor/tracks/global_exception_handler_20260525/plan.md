# Implementation Plan: Global Exception Handler

## Phase 1: Setup and Tests (Red Phase) [checkpoint: 788a018]
- [x] Task: Create tests for global exception handler 37526da
    - [x] Create `tests/test_exceptions.py` or append to an appropriate test file.
    - [x] Write a failing test that triggers an unhandled exception in a mock route and asserts the response is 500.
    - [x] Write a failing test that asserts the 500 response body follows the RFC 7807 format.
    - [x] Write a failing test that asserts no stack trace is present in the HTTP response.
    - [x] Write a test/mock to verify that the exception stack trace is logged correctly.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Setup and Tests (Red Phase)' (Protocol in workflow.md)

## Phase 2: Implementation (Green Phase)
- [ ] Task: Implement global exception handler
    - [ ] Register an exception handler for `Exception` in the FastAPI application (e.g., in `src/sciaiot/ovpncp/main.py`).
    - [ ] Construct the JSON response body according to RFC 7807 (`type`, `title`, `status`, `detail`, `instance`).
    - [ ] Implement logging within the handler to log the caught exception's stack trace.
    - [ ] Run the test suite to ensure all tests created in Phase 1 now pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Implementation (Green Phase)' (Protocol in workflow.md)