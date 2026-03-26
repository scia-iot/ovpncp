# Initial Concept
OpenVPN Control Panel for Restricted Network.

## Product Definition
The OpenVPN Control Panel (ovpncp) is a specialized API-driven platform designed to provide secure, restricted access for IoT and edge devices. It's built for users on IoT platforms, allowing for granular control over client connections, network routing, and security policies.

## Key Goals
- **IoT/Edge Access:** Enable secure, restricted communication between IoT devices and the central infrastructure.
- **Client/Network Management:** Provide a programmable API for managing clients, IP assignments, and network routes.
- **Security/Authentication:** Leverage modern authentication (Azure Entra ID) and certificate management (Azure Blob Storage) to secure the VPN infrastructure.
- **Observability:** Improve visibility into client connections and network traffic for monitoring and auditing.

## Key Features
- **FastAPI-powered API:** Programmable interface for all management tasks.
- **Restricted Network Setup:** Use IPTables and OpenVPN to define fine-grained access controls.
- **Azure Integration:** Support for Entra ID (security) and Blob Storage (certificates).
- **Certificate Management:** Automated packaging and distribution of client certificates.
- **Database Backend:** SQLModel-based persistence for client and network configurations.

## Target Audience
- Users on the IoT Platform.
- System administrators and security engineers managing IoT/edge device connectivity.

## Future Integrations
- Support for more cloud providers (AWS, GCP).
- Integration with SIEM and logging platforms for enhanced security analysis.
- Support for additional VPN protocols and identity providers.
