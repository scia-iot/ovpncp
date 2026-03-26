# Track Specification: Observability Enhancement

## Overview
- **Track ID:** observability_20260319
- **Description:** Improve the visibility and monitoring capabilities of the OpenVPN Control Panel by implementing structured logging, client connection tracking, and enhanced health metrics.

## Goals
1.  **Structured Logging:** Transition to JSON-formatted logging for better compatibility with external logging and SIEM platforms.
2.  **Client Connection History:** Track client connect and disconnect events in the database to provide a history of client activity.
3.  **Enhanced Health Checks:** Improve the `/server/health` endpoint to provide detailed information on OpenVPN service status and system resource usage.

## Components Affected
- `sciaiot.ovpncp.main`: Logger initialization and application entry point.
- `sciaiot.ovpncp.data.models`: Adding models for connection logging.
- `sciaiot.ovpncp.routes.server`: Enhancing the health check endpoint.
- `sciaiot.ovpncp.scripts`: Updating connection scripts to interact with the API.

## Requirements
- **Structured Logging:**
    - Use a standard JSON formatter for logs.
    - Support log level configuration via environment variables.
- **Connection Tracking:**
    - Create a `ConnectionHistory` model in SQLModel.
    - Implement internal API endpoints for logging connection events.
    - Update `client-connect.sh` and `client-disconnect.sh` to trigger these events via API calls.
- **Enhanced Health Metrics:**
    - Report the status of the OpenVPN service (running/stopped).
    - Report CPU, Memory, and Disk usage in the health check response.
