# Track Specification: Security Fixes (VULN-001 - VULN-007)

## Overview
This track addresses all security and privacy vulnerabilities identified in the `.gemini_security/final_report.md` report. The goal is to eliminate command injection, path traversal, and privacy leaks while strengthening the existing authentication mechanism.

## Functional Requirements

### 1. Command Injection Mitigation (VULN-001, VULN-003, VULN-004)
- Refactor all `subprocess.run` calls in `src/sciaiot/ovpncp/utils/` (`openvpn.py`, `iptables.py`, `iproute.py`) to use a list of arguments and set `shell=False`.
- Ensure all user-provided parameters (e.g., client names, network addresses) are treated as data, not as part of a shell command.

### 2. Path Traversal Mitigation (VULN-002)
- Implement strict validation for the `name` parameter in `src/sciaiot/ovpncp/utils/openvpn.py` to prevent path traversal (e.g., rejecting `..`, `/`, etc.).
- Use `os.path.basename` or similar to ensure filenames are confined to the intended directory.

### 3. Reusable Privacy Masking Utility (VULN-005, VULN-006)
- Create a new utility function `mask_sensitive` in `src/sciaiot/ovpncp/utils/logging.py` to redact sensitive patterns (SAS tokens, IP addresses) from strings.
- Update `src/sciaiot/ovpncp/middlewares/azure_storage.py` to mask SAS URLs before logging.
- Update `src/sciaiot/ovpncp/routes/client.py` to redact IP addresses from error messages.

### 4. Authentication Strengthening (VULN-007)
- Update `src/sciaiot/ovpncp/middlewares/azure_security.py` to remove the `localhost` and `127.0.0.1` bypass.
- Ensure that if authentication environment variables are missing in a production-like environment, the service fails securely or enforces mandatory authentication.

## Non-Functional Requirements
- **Test-Driven Development:** Every fix must be preceded by a failing test case that reproduces the vulnerability.
- **Code Coverage:** Maintain >80% coverage for the affected modules.

## Acceptance Criteria
- [ ] All 7 vulnerabilities from the security report are mitigated.
- [ ] `subprocess.run` is used safely across the project.
- [ ] Sensitive data is masked in logs and API responses.
- [ ] Authentication is enforced consistently, regardless of the source host.
- [ ] All unit and integration tests pass.

## Out of Scope
- Implementing a full-blown user management system (as the service relies on external Azure Entra ID roles).
- Architectural changes beyond security hardening.
