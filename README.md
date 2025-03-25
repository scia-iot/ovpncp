# OpenVPN Control Panel for Restricted Network

## Build

```shell
python -m build
```

## Install

In order to run along with OpenVPN server, the ROOT privilege is required.

For package installation, it's easier to use `pipx` with it.

```shell
sudo pipx install ovpncp-0.1.0-py3-none-any.whl
```

## OpenVPN Server Setup

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

## Basic Usage

Start the application:

```shell
sudo /root/.local/bin/ovpncp
```

**Note:** `pipx ensurepath` doesn't work here, must to run it with full path.

Or switch to ROOT user:

```shell
sudo su
ovpncp
```

Init server by calling API with cURL:

```shell
curl -X POST http://127.0.0.1:8000/server
```

Check the health of OpenVPN server:

```shell
curl -X GET http://127.0.0.1:8000/server/health
```

### Setup Client

Create the client:

```shell
curl -X POST http://127.0.0.1:8000/clients -d '{"name": "client1"}'
```

Package the client certificate:

```shell
curl -X PUT http://127.0.0.1:8000/clients/client1/package-cert
```

Download the archive:

```shell
curl -X GET http://127.0.0.1:8000/clients/client1/download-cert
```

Assign IP to the client:

```shell
curl -X POST http://127.0.0.1:8000/clients/client1/assign-ip -d '{"ip": "10.8.0.2"}'
```

### Setup Restricted Network

IMPORTANT: make sure drop all forwarding on `tun0` by default:

```shell
sudo iptables -A FORWARD -i tun0 -j DROP
```

Create the network:

```shell
curl -X POST http://127.0.0.1:8000/networks \ 
    -d '{"source_client_name": "client_1", "destination_client_name": "edge_device_1"}'
```

Drop the network:

```shell
curl -X DELETE http://127.0.0.1:8000/networks/1
```
