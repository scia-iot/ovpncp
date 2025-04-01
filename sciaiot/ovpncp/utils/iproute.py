import logging
import subprocess

logger = logging.getLogger(__name__)


def list(dev_name):
    logging.info(f'Listing ip routes for dev: {dev_name}...')
    result = subprocess.run(
        ["ip", "route", "show", "dev", dev_name], 
        capture_output=True, 
        check=True
        )
    routes = result.stdout.splitlines()
    logging.info(f'Found {len(routes)} routes for dev: {dev_name}.')
    return routes


def add(private_network, server_ip, dev_name):
    logging.info(f'Adding IP route for {private_network} via {server_ip} on {dev_name}...')
    subprocess.run(
        ['ip', 'route', 'add', private_network, 'via', server_ip, "dev", dev_name], 
        capture_output=True, 
        check=True
    )
    logging.info(f'Added IP route for {private_network} via {server_ip} on {dev_name}.')

def delete(private_network, server_ip, dev_name):
    logging.info(f'Deleting IP route for {private_network} via {server_ip} on {dev_name}...')
    subprocess.run(
        ['ip', 'route', 'del', private_network, 'via', server_ip, "dev", dev_name], 
        capture_output=True, 
        check=True
    )
    logging.info(f'Deleted IP route for {private_network} via {server_ip} on {dev_name}.')
