import logging
import re
import subprocess

logger = logging.getLogger(__name__)

status_pattern = re.compile(r'(.*?)Active: (.*?) since (.*?); (.*?) ago')
client_pattern = re.compile(r'(\w+),(\d+\.\d+\.\d+\.\d+),')
default = "N/A"


def get_server_config():
    """Get the status of the OpenVPN server."""

    logger.info("Reading OpenVPN server configuration...")
    config = {}

    with open("/etc/openvpn/server.conf", 'r') as file:
        for line in file:
            # Strip leading and trailing whitespace
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith(';'):
                continue

            # Split the line into key and value
            parts = line.split(None, 1)
            # replace all - with _
            key = parts[0].replace('-', '_')
            value = parts[1] if len(parts) > 1 else True
            config[key] = value

    logger.info("OpenVPN server configuration read successfully.")
    return config


def get_status():
    """Get the status of the OpenVPN server."""

    logger.info("Checking the status of OpenVPN server...")
    result = subprocess.run(["systemctl", "status", "openvpn@server"],
                            capture_output=True, text=True, check=True)
    lines = result.stdout.split('\n')

    if len(lines) > 3:
        match = status_pattern.match(lines[3])
        if match:
            status = match.group(2)
            time = match.group(3)
            period = match.group(4)

            logger.info(f"OpenVPN server status: {status}")
            return {"status": status, "time": time, "period": period}

    logger.error(
        "Failed to parse the output of systemctl status openvpn@server!")
    return {"status": default}


def build_client(name: str):
    """Build a client with the given name."""

    logger.info(f"Building client {name}...")
    result = subprocess.run([
        "cd", "/etc/openvpn/easy-rsa/",
        "&&",
        "./easyrsa", "--batch", "build-client-full", name, "nopass"
    ], capture_output=True, text=True, check=True)

    if result.returncode == 0:
        logger.info(
            f"Client {name} has been successfully built to OpenVPN server.")
        return True
    else:
        logger.error(f"Failed to build client {name} to OpenVPN server.")
        return False


def list_clients():
    """List the clients connected to the OpenVPN server."""

    logger.info("Retrieving the list of clients from OpenVPN server...")
    with open("/var/log/openvpn/ipp.txt", "r") as file:
        lines = file.read().splitlines()
        clients = []

        for line in lines:
            match = client_pattern.match(line)
            if match:
                name = match.group(1)
                ip = match.group(2)
                clients.append({"name": name, "ip": ip})

        logger.info(f"Found {len(clients)} client(s) of OpenVPN server.")
        return clients


def assign_client_ip(name: str, ip: str):
    """Add a client with the given name and IP address to the OpenVPN server."""

    logger.info(
        f"Adding client {name} with IP address {ip} to OpenVPN server...")
    with open("/var/log/openvpn/ipp.txt", "a") as file:
        file.write(f"{name},{ip}\n")
    logger.info(
        f"Client {name} with IP address {ip} has been successfully added to OpenVPN server.")


def list_connections():
    """List the connections made by the clients to the OpenVPN server."""

    logger.info("Retrieving the list of connections from OpenVPN server...")
    with open("/var/log/openvpn/openvpn-status.log", "r") as file:
        lines = file.read().splitlines()
        client_list_start = lines.index("OpenVPN CLIENT LIST")
        routing_table_start = lines.index("ROUTING TABLE")
        global_stats_start = lines.index("GLOBAL STATS")

        connections = []
        for i in range(client_list_start + 3, routing_table_start):
            client_info = lines[i].split(',')
            client_name = client_info[0]
            remote_address = client_info[1]
            connected_time = client_info[4]
            virtual_address = None

            for j in range(routing_table_start + 2, global_stats_start):
                route_info = lines[j].split(',')
                if route_info[1] == client_name:
                    virtual_address = route_info[0]
                    break

            if virtual_address:
                connections.append({
                    "name": client_name,
                    "ip": virtual_address,
                    "remote_address": remote_address,
                    "connected_time": connected_time
                })

        logger.info(
            f"Found {len(connections)} connection(s) from OpenVPN server.")
        return connections
