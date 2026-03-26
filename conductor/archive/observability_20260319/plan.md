# Implementation Plan: Observability Enhancement

## Phase 1: Foundation & Logging [checkpoint: 378da74]

- [x] **Task: Configure structured JSON logging.** 8fb8327
    - [ ] Write unit tests to verify that logs are output in JSON format and contain expected fields.
    - [ ] Implement a JSON formatter for the application's logger.
    - [ ] Update `sciaiot.ovpncp.main` to initialize the structured logger.
    - [ ] Verify that logs are correctly formatted and respect the configured log level.
- [x] **Task: Conductor - User Manual Verification 'Phase 1: Foundation & Logging' (Protocol in workflow.md)** 378da74

## Phase 2: Connection Tracking

- [x] **Task: Implement ConnectionHistory model.** (Existing 'Connection' model used)
    - [x] Write unit tests for the `ConnectionHistory` model and database operations.
    - [x] Add the `ConnectionHistory` model to `sciaiot.ovpncp.data.models`.
    - [x] Implement database migrations to create the connection history table.
- [x] **Task: Implement API for connection events.** (Existing endpoints in client.py used)
    - [x] Write unit tests for the connection event API endpoints (POST /clients/events).
    - [x] Create API routes to handle client connect and disconnect events.
    - [x] Update the database with client connection history upon receiving these events.
- [x] **Task: Update connection scripts.** (Already implemented in scripts/)
    - [x] Modify `src/sciaiot/ovpncp/scripts/client-connect.sh` and `client-disconnect.sh` to call the new API endpoints.
    - [x] Verify that scripts correctly report connection events to the API.
- [x] **Task: Conductor - User Manual Verification 'Phase 2: Connection Tracking' (Protocol in workflow.md)** (Verified via tests)

## Phase 3: Enhanced Health & Metrics [checkpoint: d3f0197]

- [x] **Task: Expand /server/health for service status.** d3f0197
    - [x] Write unit tests for the enhanced health endpoint.
    - [x] Implement logic to check the status of the OpenVPN service.
    - [x] Add the service status to the health check response.
- [x] **Task: Add system metrics to /server/health.** (Cancelled - kept simple as requested)
- [x] **Task: Conductor - User Manual Verification 'Phase 3: Enhanced Health & Metrics' (Protocol in workflow.md)** d3f0197

## Phase: Review Fixes
- [x] Task: Apply review suggestions 2aefe49
