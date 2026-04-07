import logging
import re
import subprocess

logger = logging.getLogger(__name__)


def validate_ip_or_net(value: str):
    """Validate that the value is a valid IP address or network CIDR."""
    # Simple regex for IPv4 or CIDR
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?$", value):
        logger.error(f"Invalid IP or network '{value}' provided!")
        raise ValueError(f"Invalid IP or network '{value}' provided!")


def validate_dev(dev_name: str):
    """Validate that the device name is safe."""
    if not re.match(r"^[a-zA-Z0-9]+$", dev_name):
        logger.error(f"Invalid device name '{dev_name}' provided!")
        raise ValueError(f"Invalid device name '{dev_name}' provided!")


def list(dev_name):
    validate_dev(dev_name)
    logging.info(f"Listing routes on {dev_name}...")
    result = subprocess.run(
        ["ip", "route", "show", "dev", dev_name],
        capture_output=True,
        text=True,
        check=True,
    )
    routes = result.stdout.splitlines()
    logging.info(f"Found {len(routes)} routes on {dev_name}.")
    return routes


def add(private_network, server_ip, dev_name):
    validate_ip_or_net(private_network)
    validate_ip_or_net(server_ip)
    validate_dev(dev_name)

    logging.info(f"Adding route for {private_network} via {server_ip} on {dev_name}...")
    subprocess.run(
        ["ip", "route", "add", private_network, "via", server_ip, "dev", dev_name],
        shell=False,
        check=True,
    )
    logging.info(f"Added route on {dev_name}.")


def delete(route, dev_name):
    """
    Delete a specific route.
    'route' usually contains the network and potentially 'via' parts.
    To be safe, we split it and validate parts.
    """
    validate_dev(dev_name)
    logging.info(f"Deleting IP route from {dev_name}: {route}...")

    # Route might be "192.168.1.0/24 via 10.8.0.1"
    parts = route.split()
    for part in parts:
        if part != "via":
            validate_ip_or_net(part)

    cmd = ["ip", "route", "del"] + parts + ["dev", dev_name]
    subprocess.run(cmd, shell=False, check=True)
    logging.info(f"Deleted IP route from {dev_name}")
