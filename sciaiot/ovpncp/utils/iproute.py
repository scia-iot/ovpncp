import logging
import subprocess

logger = logging.getLogger(__name__)


def list(dev_name):
    command = [
        "ip", "route", 
        "show", 
        "dev", dev_name
    ]
    
    logger.info(f"Listing routes: {' '.join(command)}")
    routes = subprocess.run(command, capture_output=True, shell=True, check=True).stdout.splitlines()
    logger.info(f"Found {len(routes)} routes.")
    return routes


def add(private_network, server_ip, dev_name):
    command = [
        "ip", "route", 
        "add", private_network,
        "via", server_ip, 
        "dev", dev_name
    ]

    logger.info(f"Adding route: {' '.join(command)}")
    subprocess.run(command, capture_output=True, shell=True, check=True)
    logger.info("Route added successfully.")


def delete(private_network, server_ip, dev_name):
    command = [
        "ip", "route", 
        "del", private_network,
        "via", server_ip, 
        "dev", dev_name
    ]
    
    logger.info(f"Deleting route: {' '.join(command)}")
    subprocess.run(command, capture_output=True, shell=True, check=True)
    logger.info("Route deleted successfully.")
