# Specification: Import Existing OpenVPN Clients

## Overview
Add a new API endpoint to import existing OpenVPN clients into the control panel's database. This feature is crucial for migrating existing setups or synchronizing the database with the file system state.

## Functional Requirements
1. **Source of Truth:** The API must scan the Easy-RSA directory (e.g., `/etc/openvpn/easy-rsa/pki/issued` or the relevant `easy-rsa` path containing `.crt` files) to identify existing client certificates.
2. **Data Extraction:** For each discovered certificate, the API must parse the file to extract details to populate the `Client` and `Cert` SQL models, including:
   - `name` (derived from the Common Name / filename)
   - `issued_by`, `issued_to`, `issued_on`, `expires_on` (from the X.509 certificate metadata)
   - `revoked` status (default to False, or checked against `index.txt`/CRL if applicable).
3. **Collision Handling (Update Existing):** If a client with the same name already exists in the database, the import process must update the existing `Client` and associated `Cert` records with the data read from the certificate directory.
4. **API Endpoint:** A secured endpoint (e.g., `POST /api/clients/import`) must be exposed to trigger this process.

## Non-Functional Requirements
- **Performance:** The import process should handle a directory with potentially hundreds of certificates efficiently.
- **Security:** The endpoint must be protected by the standard Azure Entra ID authentication middleware.

## Acceptance Criteria
- A `POST /api/clients/import` API endpoint exists to trigger the import.
- When called, it successfully reads all client `.crt` files from the `/etc/openvpn/easy-rsa` directory structure.
- It parses X.509 certificate data using the `cryptography` library.
- It creates new `Client` and `Cert` database records for missing clients.
- It updates existing `Client` and `Cert` records if they already exist.
- It returns a JSON summary of the import operation (e.g., `{"added": X, "updated": Y}`).