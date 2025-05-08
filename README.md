# OpenVPN Control Panel for Restricted Network

[![Tests](https://github.com/scia-iot/ovpncp/actions/workflows/tests.yml/badge.svg)](https://github.com/scia-iot/ovpncp/actions/workflows/tests.yml)
[![CodeQL Advanced](https://github.com/scia-iot/ovpncp/actions/workflows/codeql.yml/badge.svg)](https://github.com/scia-iot/ovpncp/actions/workflows/codeql.yml)
[![Package](https://github.com/scia-iot/ovpncp/actions/workflows/package.yml/badge.svg)](https://github.com/scia-iot/ovpncp/actions/workflows/package.yml)

## Installation

In order to run along with OpenVPN server, the ROOT privilege is required.

```shell
sudo pipx install ovpncp
```

## OpenVPN Server Setup

Make sure the `client-to-client` directive is disabled:

```shell
;client-to-client
```

Enable CCD & make it exclusive:

```shell
client-config-dir /etc/openvpn/ccd
ccd_exclusive
```

Enable the scripts of client connection:

```shell
client-connect /opt/ovpncp/scripts/client-connect.sh
client-disconnect /opt/ovpncp/scripts/client-disconnect.sh
```

Start the application:

```shell
sudo -i ovpncp
```

Restart the server:

```shell
sudo systemctl restart openvpn
```

## Basic Usage

Init server by calling API with cURL:

```shell
curl -X POST http://127.0.0.1:8000/server
```

Check the health of OpenVPN server:

```shell
curl -X GET http://127.0.0.1:8000/server/health
```

### Client Setup

Create a client:

```shell
curl -X POST http://127.0.0.1:8000/clients \ 
    -d '{"name": "client_1"}'
```

Create a gateway client with the private network behind it:

```shell
curl -X POST http://127.0.0.1:8000/clients \ 
--data-binary @- << EOF 
{
    "name": "gateway_1", 
    "cidr": "192.168.1.0/24"
}
EOF
```

Package the client certificate:

```shell
curl -X PUT http://127.0.0.1:8000/clients/client_1/package-cert
```

Download the archive:

```shell
curl -X GET http://127.0.0.1:8000/clients/client_1/download-cert
```

Assign IP to the client:

```shell
curl -X PUT http://127.0.0.1:8000/clients/client_1/assign-ip \ 
    -d '{"ip": "10.8.0.2"}'
```

Unassign IP from the client:

```shell
curl -X DELETE http://127.0.0.1:8000/clients/client_1/unassign-ip
```

### Restricted Network Setup

IMPORTANT:
make sure drop all forwarding on `tun0` by default:

```shell
sudo iptables -A FORWARD -i tun0 -j DROP
```

Create a restricted network between two clients:

```shell
curl -X POST http://127.0.0.1:8000/networks \ 
--data-binary @- << EOF 
{
    "source_name": "client_1", 
    "destination_name": "edge_device_1",
}
EOF
```

Create a restricted network between a client and a gateway:

```shell
curl -X POST http://127.0.0.1:8000/networks \ 
--data-binary @- << EOF 
{
    "source_name": "client_1", 
    "destination_name": "edge_gateway_1", 
    "private_network_addresses": "192.168.1.1,192.168.1.2,192.168.1.3"
}
EOF
```

Add an IP route for allowing traffic on the OpenVPN server:

```shell
curl -X POST http://127.0.0.1:8000/server/routes \
--data-binary @- << EOF 
{
    "network": 192.168.1.0/24"
}
EOF
```

Drop the network:

```shell
curl -X DELETE http://127.0.0.1:8000/networks/1
```

### [Optional] Enable Security with Azure Entra ID

Register this app on Azure Entra ID first, then sets three ENVs to enable the security middleware:

1. `TENANT_ID` - the tenant ID of Azure Entra ID directory.

2. `APP_CLIENT_ID` - the application (client) ID of this app that registered.

3. `APP_ROLE` - the app role assigned by this app.

Notice: for client app, two things must be configured on the client app registration:

1. enable the optional claim `aud` of token type `Access` on the `Token configuration`;

2. add the permission of this app on the `API permissions`.

### [Optional] Enable Cert Management with Azure Blob Storage

1. Create a storage account on Azure Portal.

2. Create a container named `ovpncp` on the storage account.

3. Obtain the access key and set it to the `AZURE_STORAGE_CONNECTION_STRING`
