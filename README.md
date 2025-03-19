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

## Usage

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

### About Restricted Network

IMPORTANT: make sure drop all forwarding by default:

```shell
sudo iptables -A FORWARD -i tun0 -j DROP
```
