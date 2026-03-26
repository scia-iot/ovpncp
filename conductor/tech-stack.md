# Technology Stack

## Core Language & Runtime
- **Language:** Python 3.14+
- **Runtime:** CPython

## Web Framework & API
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework for building APIs.
- **Web Server:** [Uvicorn](https://www.uvicorn.org/) - ASGI server implementation.
- **Serialization:** [Pydantic](https://docs.pydantic.dev/) (via FastAPI/SQLModel) - Data validation and settings management.

## Database & Persistence
- **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) - Python library for interacting with SQL databases using Python objects.
- **Database:** Support for SQLite (default), PostgreSQL, and MySQL (via optional dependencies).

## Security & Authentication
- **Security Middleware:** Custom Azure Entra ID integration.
- **Token Handling:** [python-jose](https://github.com/mpdavis/python-jose) - JOSE (JSON Object Signing and Encryption) implementation.
- **Cryptography:** [cryptography](https://cryptography.io/) - Recipe-based security for cryptographic primitives.

## Storage & Integration
- **Cloud Storage:** [Azure Blob Storage](https://azure.microsoft.com/en-us/services/storage/blobs/) - Used for certificate management and distribution.
- **Cloud Identity:** [Azure Entra ID](https://www.microsoft.com/en-us/security/business/identity-access-management/azure-ad) - Used for API security and user authentication.

## Networking & System
- **VPN:** [OpenVPN](https://openvpn.net/) - Core VPN server and client management.
- **Firewall/NAT:** `iptables` - Used for defining restricted network access policies.
- **IP Routing:** `iproute2` - Used for managing network routes on the server.

## Configuration & Tooling
- **Configuration:** [PyYAML](https://pyyaml.org/) - Used for reading `log.yml` and potentially other YAML-based configs.
- **Packaging:** [setuptools](https://github.com/pypa/setuptools) - Standard Python packaging tool.
- **Distribution:** [pipx](https://github.com/pypa/pipx) - Used for installing and running Python applications in isolated environments.
