# Specification: Global Exception Handler

## Overview
Implement a global exception handler in the FastAPI application to manage unhandled server errors (500 Internal Server Error) securely and consistently.

## Functional Requirements
- **Catch-All Handler:** Intercept all otherwise unhandled exceptions across the API.
- **RFC 7807 Format:** Format the error responses to adhere to the RFC 7807 Problem Details for HTTP APIs standard.
    - Expected fields: `type` (URI reference), `title` (short summary), `status` (HTTP status code), `detail` (human-readable explanation), `instance` (URI reference of occurrence).
- **Environment-Aware Detail:** Never expose stack traces or sensitive internal details to the client in the response.
- **Targeted Logging:** Log the full exception, including the stack trace, only for unexpected 500 internal server errors.

## Non-Functional Requirements
- **Security:** Ensure no sensitive information is leaked through error messages.
- **Consistency:** Ensure the API error format matches standard HTTP expectations.

## Acceptance Criteria
- [ ] Any unhandled exception raised within a route results in a 500 Internal Server Error response.
- [ ] The response body strictly follows the RFC 7807 JSON format.
- [ ] No stack traces are returned in the HTTP response.
- [ ] The full exception stack trace is logged to the application logs for debugging purposes.

## Out of Scope
- Custom domain exceptions and validation error (422) overrides are out of scope for this track.