# Implementation Plan: Security Fixes

This plan outlines the steps to remediate all 7 security and privacy vulnerabilities identified in the security report.

## Phase 1: Foundation & Privacy Utility [checkpoint: 05b63a9]
- [x] Task: Write failing tests for `mask_sensitive` utility in `tests/test_logging.py`. [5a739bd]
- [x] Task: Implement `mask_sensitive` utility in `src/sciaiot/ovpncp/utils/logging.py` to redact SAS tokens and IP addresses. [5a739bd]
- [x] Task: Conductor - User Manual Verification 'Foundation & Privacy Utility' (Protocol in workflow.md)

## Phase 2: Command Injection Remediation [checkpoint: a3ba695]
- [x] Task: Write failing tests in `tests/test_openvpn.py` to reproduce command injection in `openvpn.py`. [9d97d29]
- [x] Task: Refactor `src/sciaiot/ovpncp/utils/openvpn.py` to use `subprocess.run` with a list of arguments and `shell=False`. [9d97d29]
- [x] Task: Write failing tests in `tests/test_iptables.py` to reproduce command injection in `iptables.py`. [4abd967]
- [x] Task: Refactor `src/sciaiot/ovpncp/utils/iptables.py` to use `subprocess.run` with a list of arguments and `shell=False`. [4abd967]
- [x] Task: Write failing tests in `tests/test_iproute.py` to reproduce command injection in `iproute.py`. [26edc99]
- [x] Task: Refactor `src/sciaiot/ovpncp/utils/iproute.py` to use `subprocess.run` with a list of arguments and `shell=False`. [26edc99]
- [x] Task: Conductor - User Manual Verification 'Command Injection Remediation' (Protocol in workflow.md)

## Phase 3: Path Traversal & Privacy Mitigation [checkpoint: 14b87ee]
- [x] Task: Write failing tests in `tests/test_openvpn.py` to reproduce path traversal in `openvpn.py`. [1f0080f]
- [x] Task: Implement `name` validation and path sanitization in `src/sciaiot/ovpncp/utils/openvpn.py`. [1f0080f]
- [x] Task: Write failing tests in `tests/test_api.py` to reproduce privacy leaks (SAS URL in logs, IP in error message). [1f0080f]
- [x] Task: Update `src/sciaiot/ovpncp/middlewares/azure_storage.py` to mask SAS URLs in logs. [1f0080f]
- [x] Task: Update `src/sciaiot/ovpncp/routes/client.py` to redact IP addresses in error messages. [1f0080f]
- [x] Task: Conductor - User Manual Verification 'Path Traversal & Privacy Mitigation' (Protocol in workflow.md)

## Phase 4: Authentication Strengthening [checkpoint: 7660840]
- [x] Task: Write failing tests in `tests/test_security.py` to reproduce bypass using `localhost` or missing environment variables. [0b9de91]
- [x] Task: Update `src/sciaiot/ovpncp/middlewares/azure_security.py` to remove host-based bypass and enforce mandatory authentication if configured. [0b9de91]
- [x] Task: Conductor - User Manual Verification 'Authentication Strengthening' (Protocol in workflow.md)
