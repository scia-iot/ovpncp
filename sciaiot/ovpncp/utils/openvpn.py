import contextlib
import logging
import os
import re
import subprocess
import zipfile

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)

status_pattern = re.compile(r'(.*?)Active: (.*?) since (.*?); (.*?) ago')
client_pattern = re.compile(r'(\w+),(\d+\.\d+\.\d+\.\d+)')
default = 'N/A'
openvpn_dir = '/etc/openvpn'
openvpn_log_dir = '/var/log/openvpn'
easyrsa_dir = f'{openvpn_dir}/easy-rsa'

def get_server_config():
    '''Get the status of the OpenVPN server.'''

    logger.info('Reading OpenVPN server configuration...')
    config = {}

    with open(f'{openvpn_dir}/server.conf', 'r') as file:
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

    logger.info('OpenVPN server configuration read successfully.')
    return config


def get_status():
    '''Get the status of the OpenVPN server.'''

    logger.info('Checking the status of OpenVPN server...')
    result = subprocess.run(['systemctl', 'status', 'openvpn@server'],
                            capture_output=True, text=True, check=False)

    match = status_pattern.search(result.stdout)
    if match:
        status = match.group(2)
        time = match.group(3)
        period = match.group(4)

        logger.info(f'OpenVPN server status: {status}')
        return {'status': status, 'time': time, 'period': period}

    logger.error(
        'Failed to parse the output of systemctl status openvpn@server!')
    return {'status': default}


def list_clients():
    '''List the clients connected to the OpenVPN server.'''

    logger.info('Retrieving the list of clients from OpenVPN server...')
    with open(f'{openvpn_log_dir}/ipp.txt', 'r') as file:
        lines = file.read().splitlines()
        clients = []

        for line in lines:
            match = client_pattern.match(line)
            if match:
                name = match.group(1)
                ip = match.group(2)
                clients.append({'name': name, 'ip': ip})

        logger.info(f'Found {len(clients)} client(s) of OpenVPN server.')
        return clients


def build_client(name: str):
    '''Build a client with the given name.'''

    logger.info(f'Building client {name}...')
    result = subprocess.run(
        f'./easyrsa --batch build-client-full {name} nopass',
        cwd=easyrsa_dir,
        shell=True, capture_output=True, text=True, check=True
    )

    if result.returncode == 0:
        logger.info(
            f'Client {name} has been successfully built to OpenVPN server.')
        return True
    else:
        logger.error(f'Failed to build client {name} to OpenVPN server!')
        return False


def read_client_cert(name: str) -> dict:
    '''Read the client certificate for the given client name and extract issued and expired times, issued_to, and issued_by.'''
    
    try:
        logger.info(f'Reading certificate for client {name}...')
        cert_path = os.path.join(f'{easyrsa_dir}/pki/issued', f'{name}.crt')
        
        with open(cert_path, 'rb') as file:
            cert_content = file.read()
            cert = x509.load_pem_x509_certificate(cert_content, default_backend())
            issued_by = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            issued_to = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            issued_on = cert.not_valid_before
            expires_on = cert.not_valid_after
            
            logger.info(f'Successfully read certificate for client {name}.')
            return {
                'issued_by': issued_by,
                'issued_to': issued_to,
                'issued_on': issued_on,
                'expires_on': expires_on,
            }
    except Exception as e:
        logger.error(f'Failed to read certificate for client {name}: {e}')
        return {}


def package_client_cert(name: str, output_dir: str):
    '''Package the client certificate and key files into a tar archive.'''
    
    cert_dir = f'{easyrsa_dir}/pki'
    ca = f'{cert_dir}/ca.crt'
    pk = f'{cert_dir}/private/{name}.key'
    cert = f'{cert_dir}/issued/{name}.crt'
    archive = os.path.join(output_dir, f'{name}.zip')
    
    with contextlib.suppress(FileNotFoundError):
        os.remove(archive)
    
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as file:
        file.write(ca, arcname=os.path.basename(ca))
        file.write(pk, arcname=os.path.basename(pk))
        file.write(cert, arcname=os.path.basename(cert))
    
    logger.info(f'Successfully packaged client {name} certificate into {archive}.')
    return archive

def renew_client_cert(name: str) -> dict:
    '''Renew the client certificate for the given client name and read the renewed certificate details.'''

    logger.info(f'Renewing client {name} certificate...')
    result = subprocess.run(
        f'./easyrsa --batch revoke-renewed {name}', 
        cwd=easyrsa_dir,
        shell=True, capture_output=True, text=True, check=True
    )

    if result.returncode == 0:
        logger.info(f'Client {name} certificate has been successfully renewed.')
        cert_details = read_client_cert(name)
        return cert_details
    else:
        logger.error(f'Failed to renew client {name} certificate!')
        return {}


def revoke_client(name: str):
    '''Revoke the client certificate for the given client name and generate a new CRL to confirm the revocation.'''

    logger.info(f'Revoking client {name}...')
    result = subprocess.run(
        f'./easyrsa --batch revoke {name}', 
        cwd=easyrsa_dir, 
        shell=True, capture_output=True, text=True, check=True
    )

    if result.returncode == 0:
        logger.info(f'Client {name} has been successfully revoked.')
        return True
    else:
        logger.error(f'Failed to revoke client {name}!')
        return False


def generate_crl() -> bool:
    '''Generate a new CRL.'''
    logger.info('Generating CRL...')
    result = subprocess.run(
        './easyrsa --batch gen-crl', 
        cwd=easyrsa_dir, 
        shell=True, capture_output=True, text=True, check=True
    )

    if result.returncode == 0:
        logger.info('CRL generated successfully.')
        return True
    else:
        logger.error('Failed to generate CRL.')
        return False


def assign_client_ip(name: str, ip: str):
    '''Add a client with the given name and IP address to the OpenVPN server.'''

    logger.info(
        f'Adding client {name} with IP address {ip} to OpenVPN server...')
    with open(f'{openvpn_log_dir}/ipp.txt', 'a') as file:
        file.write(f'{name},{ip}\n')
    logger.info(
        f'Client {name} with IP address {ip} has been successfully added to OpenVPN server.')


def unassign_client_ip(name: str, ip: str):
    '''Remove a client with the given name and IP address from the OpenVPN server.'''

    logger.info(f'Removing client {name} with IP address {ip} from OpenVPN server...')

    file_path = f'{openvpn_log_dir}/ipp.txt'
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip() != f'{name},{ip}':
                file.write(line)

    logger.info(f'Client {name} with IP address {ip} has been successfully removed from OpenVPN server.')


def list_connections():
    '''List the connections made by the clients to the OpenVPN server.'''

    logger.info('Retrieving the list of connections from OpenVPN server...')
    with open(f'{openvpn_log_dir}/openvpn-status.log', 'r') as file:
        lines = file.read().splitlines()
        client_list_start = lines.index('OpenVPN CLIENT LIST')
        routing_table_start = lines.index('ROUTING TABLE')
        global_stats_start = lines.index('GLOBAL STATS')

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
                    'name': client_name,
                    'ip': virtual_address,
                    'remote_address': remote_address,
                    'connected_time': connected_time
                })

        logger.info(
            f'Found {len(connections)} connection(s) from OpenVPN server.')
        return connections
