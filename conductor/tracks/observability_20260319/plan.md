# Implementation Plan: Observability Enhancement

## Phase 1: Foundation & Logging

- [x] **Task: Configure structured JSON logging.** 8fb8327
    - [ ] Write unit tests to verify that logs are output in JSON format and contain expected fields.
    - [ ] Implement a JSON formatter for the application's logger.
    - [ ] Update `sciaiot.ovpncp.main` to initialize the structured logger.
    - [ ] Verify that logs are correctly formatted and respect the configured log level.
- [~] **Task: Conductor - User Manual Verification 'Phase 1: Foundation & Logging' (Protocol in workflow.md)**

## Phase 2: Connection Tracking

- [ ] **Task: Implement ConnectionHistory model.**
    - [ ] Write unit tests for the `ConnectionHistory` model and database operations.
    - [ ] Add the `ConnectionHistory` model to `sciaiot.ovpncp.data.models`.
    - [ ] Implement database migrations to create the connection history table.
- [ ] **Task: Implement API for connection events.**
    - [ ] Write unit tests for the connection event API endpoints (POST /clients/events).
    - [ ] Create API routes to handle client connect and disconnect events.
    - [ ] Update the database with client connection history upon receiving these events.
- [ ] **Task: Update connection scripts.**
    - [ ] Modify `src/sciaiot/ovpncp/scripts/client-connect.sh` and `client-disconnect.sh` to call the new API endpoints.
    - [ ] Verify that scripts correctly report connection events to the API.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Connection Tracking' (Protocol in workflow.md)**

## Phase 3: Enhanced Health & Metrics

- [ ] **Task: Expand /server/health for service status.**
    - [ ] Write unit tests for the enhanced health endpoint.
    - [ ] Implement logic to check the status of the OpenVPN service (e.g., by checking the process or service status).
    - [ ] Add the service status to the health check response.
- [ ] **Task: Add system metrics to /server/health.**
    - [ ] Write unit tests for the system metrics logic.
    - [ ] Implement logic to retrieve system metrics (CPU, Memory, Disk usage).
    - [ ] Add these metrics to the health check response.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: Enhanced Health & Metrics' (Protocol in workflow.md)**
