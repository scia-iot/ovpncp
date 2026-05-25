# Implementation Plan: Import Existing OpenVPN Clients

## Phase 1: Certificate Discovery Utility [checkpoint: a6347c6]
- [x] Task: Write tests for a new function `list_client_certs` in `utils/openvpn.py` that returns a list of all client names from the issued directory. 1e749dd
- [x] Task: Implement `list_client_certs` to scan `/etc/openvpn/easy-rsa/pki/issued/` for `.crt` files and return the base names (Common Names). 1e749dd
- [x] Task: Conductor - User Manual Verification 'Phase 1: Certificate Discovery Utility' (Protocol in workflow.md) a6347c6

## Phase 2: API Endpoint and Database Upsert [checkpoint: f176f3a]
- [x] Task: Write tests for the `POST /api/clients/import` endpoint, ensuring it correctly creates or updates `Client` and `Cert` models. 03f7cd6
- [x] Task: Implement the `POST /api/clients/import` endpoint in `routes/client.py`, utilizing `list_client_certs` and the existing `read_client_cert` function to handle the database upsert logic. 03f7cd6
- [x] Task: Conductor - User Manual Verification 'Phase 2: API Endpoint and Database Upsert' (Protocol in workflow.md) f176f3a