import logging
import subprocess

logger = logging.getLogger(__name__)


def list(dev_name):
    logging.info(f'Listing routes on {dev_name}...')
    result = subprocess.run(
        ['ip', 'route', 'show', 'dev', dev_name],
        capture_output=True,
        text=True,
        check=True
        )
    routes = result.stdout.splitlines()
    logging.info(f'Found {len(routes)} routes on {dev_name}.')
    return routes


def add(private_network, server_ip, dev_name):
    logging.info(f'Adding route for {private_network} via {server_ip} on {dev_name}...')
    subprocess.run(
        f'ip route add {private_network} via {server_ip} dev {dev_name}', 
        shell=True,
        check=True
    )
    logging.info(f'Added route on {dev_name}.')


def delete(route, dev_name):
    logging.info(f'Deleting IP route from {dev_name}: {route}...')
    subprocess.run(
        f'ip route del {route} dev {dev_name}', 
        shell=True,
        check=True
    )
    logging.info(f'Deleted IP route from {dev_name}')
