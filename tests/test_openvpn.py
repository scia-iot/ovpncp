import zipfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

from sciaiot.ovpncp.utils.openvpn import (
    add_iroute,
    assign_client_ip,
    build_client,
    generate_crl,
    get_server_config,
    get_status,
    list_connections,
    package_client_cert,
    pull_client_routes,
    push_client_routes,
    read_client_cert,
    remove_iroute,
    renew_client_cert,
    revoke_client,
    unassign_client_ip,
)

server_config_lines = """
# This file is for the server side              #
# of a many-clients <-> one-server              #
# OpenVPN configuration.                        #
#                                               #
# OpenVPN also supports                         #
# single-machine <-> single-machine             #
# configurations (See the Examples page         #
# on the web site for more info).               #
#                                               #
# This config should work on Windows            #
# or Linux/BSD systems.  Remember on            #
# Windows to quote pathnames and use            #
# double backslashes, e.g.:                     #
# "C:\\Program Files\\OpenVPN\\config\\foo.key" #
#                                               #
# Comments are preceded with "#" or ";"         #
#################################################

# Which local IP address should OpenVPN
# listen on? (optional)
;local a.b.c.d

# Which TCP/UDP port should OpenVPN listen on?
# If you want to run multiple OpenVPN instances
# on the same machine, use a different port
# number for each one.  You will need to
# open up this port on your firewall.
port 1194

# TCP or UDP server?
;proto tcp
proto udp

# "dev tun" will create a routed IP tunnel,
# "dev tap" will create an ethernet tunnel.
# Use "dev tap0" if you are ethernet bridging
# and have precreated a tap0 virtual interface
# and bridged it with your ethernet interface.
# If you want to control access policies
# over the VPN, you must create firewall
# rules for the TUN/TAP interface.
# On non-Windows systems, you can give
# an explicit unit number, such as tun0.
# On Windows, use "dev-node" for this.
# On most systems, the VPN will not function
# unless you partially or fully disable/open
# the firewall for the TUN/TAP interface.
;dev tap
dev tun

# Windows needs the TAP-Win32 adapter name
# from the Network Connections panel if you
# have more than one.
# You may need to selectively disable the
# Windows firewall for the TAP adapter.
# Non-Windows systems usually don"t need this.
;dev-node MyTap

# SSL/TLS root certificate (ca), certificate
# (cert), and private key (key).  Each client
# and the server must have their own cert and
# key file.  The server and all clients will
# use the same ca file.
#
# See the "easy-rsa" project at
# https://github.com/OpenVPN/easy-rsa
# for generating RSA certificates
# and private keys.  Remember to use
# a unique Common Name for the server
# and each of the client certificates.
#
# Any X509 key management system can be used.
# OpenVPN can also use a PKCS #12 formatted key file
# (see "pkcs12" directive in man page).
#
# If you do not want to maintain a CA
# and have a small number of clients
# you can also use self-signed certificates
# and use the peer-fingerprint option.
# See openvpn-examples man page for a
# configuration example.
ca ca.crt
cert server.crt
key server.key

# Diffie hellman parameters.
# Generate your own with:
#   openssl dhparam -out dh2048.pem 2048
dh dh2048.pem

# Allow to connect to really old OpenVPN versions
# without AEAD support (OpenVPN 2.3.x or older)
# This adds AES-256-CBC as fallback cipher and
# keeps the modern ciphers as well.
;data-ciphers AES-256-GCM:AES-128-GCM:?CHACHA20-POLY1305:AES-256-CBC
data-ciphers-fallback AES-256-CBC

# Network topology
# Should be subnet (addressing via IP)
# unless Windows clients v2.0.9 and lower have to
# be supported (then net30, i.e. a /30 per client)
# Defaults to net30 (not recommended)
topology subnet

# Configure server mode and supply a VPN subnet
# for OpenVPN to draw client addresses from.
# The server will take 10.8.0.1 for itself,
# the rest will be made available to clients.
# Each client will be able to reach the server
# on 10.8.0.1. Comment this line out if you are
# ethernet bridging. See the man page for more info.
server 10.8.0.0 255.255.255.0

# Maintain a record of client <-> virtual IP address
# associations in this file.  If OpenVPN goes down or
# is restarted, reconnecting clients can be assigned
# the same virtual IP address from the pool that was
# previously assigned.
ifconfig-pool-persist /var/log/openvpn/ipp.txt

# Configure server mode for ethernet bridging.
# You must first use your OS"s bridging capability
# to bridge the TAP interface with the ethernet
# NIC interface.  Then you must manually set the
# IP/netmask on the bridge interface, here we
# assume 10.8.0.4/255.255.255.0.  Finally we
# must set aside an IP range in this subnet
# (start=10.8.0.50 end=10.8.0.100) to allocate
# to connecting clients.  Leave this line commented
# out unless you are ethernet bridging.
;server-bridge 10.8.0.4 255.255.255.0 10.8.0.50 10.8.0.100

# Configure server mode for ethernet bridging
# using a DHCP-proxy, where clients talk
# to the OpenVPN server-side DHCP server
# to receive their IP address allocation
# and DNS server addresses.  You must first use
# your OS"s bridging capability to bridge the TAP
# interface with the ethernet NIC interface.
# Note: this mode only works on clients (such as
# Windows), where the client-side TAP adapter is
# bound to a DHCP client.
;server-bridge

# Push routes to the client to allow it
# to reach other private subnets behind
# the server.  Remember that these
# private subnets will also need
# to know to route the OpenVPN client
# address pool (10.8.0.0/255.255.255.0)
# back to the OpenVPN server.
;push "route 192.168.10.0 255.255.255.0"
;push "route 192.168.20.0 255.255.255.0"

# To assign specific IP addresses to specific
# clients or if a connecting client has a private
# subnet behind it that should also have VPN access,
# use the subdirectory "ccd" for client-specific
# configuration files (see man page for more info).
client-config-dir ccd
ccd-exclusive

# EXAMPLE: Suppose the client
# having the certificate common name "Thelonious"
# also has a small subnet behind his connecting
# machine, such as 192.168.40.128/255.255.255.248.
# First, uncomment out these lines:
;client-config-dir ccd
;route 192.168.40.128 255.255.255.248
# Then create a file ccd/Thelonious with this line:
#   iroute 192.168.40.128 255.255.255.248
# This will allow Thelonious" private subnet to
# access the VPN.  This example will only work
# if you are routing, not bridging, i.e. you are
# using "dev tun" and "server" directives.

# EXAMPLE: Suppose you want to give
# Thelonious a fixed VPN IP address of 10.9.0.1.
# First uncomment out these lines:
;client-config-dir ccd
;route 10.9.0.0 255.255.255.252
# Then add this line to ccd/Thelonious:
#   ifconfig-push 10.9.0.1 10.9.0.2

# Suppose that you want to enable different
# firewall access policies for different groups
# of clients.  There are two methods:
# (1) Run multiple OpenVPN daemons, one for each
#     group, and firewall the TUN/TAP interface
#     for each group/daemon appropriately.
# (2) (Advanced) Create a script to dynamically
#     modify the firewall in response to access
#     from different clients.  See man
#     page for more info on learn-address script.
;learn-address ./script

# If enabled, this directive will configure
# all clients to redirect their default
# network gateway through the VPN, causing
# all IP traffic such as web browsing and
# and DNS lookups to go through the VPN
# (The OpenVPN server machine may need to NAT
# or bridge the TUN/TAP interface to the internet
# in order for this to work properly).
;push "redirect-gateway def1 bypass-dhcp"

# Certain Windows-specific network settings
# can be pushed to clients, such as DNS
# or WINS server addresses.  CAVEAT:
# http://openvpn.net/faq.html#dhcpcaveats
# The addresses below refer to the public
# DNS servers provided by opendns.com.
;push "dhcp-option DNS 208.67.222.222"
;push "dhcp-option DNS 208.67.220.220"

# Uncomment this directive to allow different
# clients to be able to "see" each other.
# By default, clients will only see the server.
# To force clients to only see the server, you
# will also need to appropriately firewall the
# server"s TUN/TAP interface.
;client-to-client

# Uncomment this directive if multiple clients
# might connect with the same certificate/key
# files or common names.  This is recommended
# only for testing purposes.  For production use,
# each client should have its own certificate/key
# pair.
#
# IF YOU HAVE NOT GENERATED INDIVIDUAL
# CERTIFICATE/KEY PAIRS FOR EACH CLIENT,
# EACH HAVING ITS OWN UNIQUE "COMMON NAME",
# UNCOMMENT THIS LINE.
;duplicate-cn

# The keepalive directive causes ping-like
# messages to be sent back and forth over
# the link so that each side knows when
# the other side has gone down.
# Ping every 10 seconds, assume that remote
# peer is down if no ping received during
# a 120 second time period.
keepalive 10 120

# For extra security beyond that provided
# by SSL/TLS, create an "HMAC firewall"
# to help block DoS attacks and UDP port flooding.
#
# Generate with:
#   openvpn --genkey tls-auth ta.key
#
# The server and each client must have
# a copy of this key.
# The second parameter should be "0"
# on the server and "1" on the clients.
;tls-auth ta.key 0 # This file is secret

# The maximum number of concurrently connected
# clients we want to allow.
;max-clients 100

# It"s a good idea to reduce the OpenVPN
# daemon"s privileges after initialization.
#
# You can uncomment this on non-Windows
# systems after creating a dedicated user.
;user openvpn
;group openvpn

# The persist options will try to avoid
# accessing certain resources on restart
# that may no longer be accessible because
# of the privilege downgrade.
persist-key
persist-tun

# Output a short status file showing
# current connections, truncated
# and rewritten every minute.
status /var/log/openvpn/openvpn-status.log

# By default, log messages will go to the syslog (or
# on Windows, if running as a service, they will go to
# the "\\Program Files\\OpenVPN\\log" directory).
# Use log or log-append to override this default.
# "log" will truncate the log file on OpenVPN startup,
# while "log-append" will append to it.  Use one
# or the other (but not both).
log         /var/log/openvpn/openvpn.log
;log-append  /var/log/openvpn/openvpn.log

# Set the appropriate level of log
# file verbosity.
#
# 0 is silent, except for fatal errors
# 4 is reasonable for general usage
# 5 and 6 can help to debug connection problems
# 9 is extremely verbose
verb 3

# Silence repeating messages.  At most 20
# sequential messages of the same message
# category will be output to the log.
;mute 20

# Notify the client that when the server restarts so it
# can automatically reconnect.
explicit-exit-notify 1

client-connect /opt/ovpncp/client-connect.sh
client-disconnect /opt/ovpncp/client-disconnect.sh
script-security 2
"""


@patch('builtins.open', new_callable=mock_open, read_data=server_config_lines)
def test_get_server_config(mock_open):
    configs = get_server_config()
    assert configs is not None
    assert len(configs) == 23

    mock_open.assert_called_with('/etc/openvpn/server.conf', 'r')


server_status_active = """
● openvpn@server.service - OpenVPN connection to server
    Loaded: loaded (/usr/lib/systemd/system/openvpn@.service; enabled; preset: enabled)
    Active: active (running) since Mon 2025-01-13 08:15:17 UTC; 15s ago
    """


@patch('subprocess.run', return_value=MagicMock(stdout=server_status_active))
def test_get_status_active(mock_run):
    status = get_status()
    assert status is not None
    assert status['status'] == 'active (running)'
    assert status['time'] == 'Mon 2025-01-13 08:15:17 UTC'
    assert status['period'] == '15s'

    mock_run.assert_called_once_with(
        ['systemctl', 'status', 'openvpn'], capture_output=True, text=True, check=True)


server_status_inactive = """
○ openvpn@server.service - OpenVPN connection to server
    Loaded: loaded (/usr/lib/systemd/system/openvpn@.service; enabled; preset: enabled)
    Active: inactive (dead) since Mon 2025-01-13 08:16:12 UTC; 29s ago
    """


@patch('subprocess.run', return_value=MagicMock(stdout=server_status_inactive))
def test_get_status_inactive(mock_run):
    status = get_status()
    assert status is not None
    assert status['status'] == 'inactive (dead)'
    assert status['time'] == 'Mon 2025-01-13 08:16:12 UTC'
    assert status['period'] == '29s'

    mock_run.assert_called_once_with(
        ['systemctl', 'status', 'openvpn'], capture_output=True, text=True, check=True)


@patch('subprocess.run')
def test_get_status_wrong(mock_run):
    mock_run.return_value = MagicMock(stdout='')

    status = get_status()
    assert status is not None
    assert status['status'] == 'N/A'

    mock_run.assert_called_once_with(
        ['systemctl', 'status', 'openvpn'], capture_output=True, text=True, check=True)


@patch('subprocess.run', return_value=MagicMock(returncode=0))
def test_build_client(mock_run):
    success = build_client('client')
    assert success is True

    mock_run.assert_called_once_with(
        './easyrsa --batch build-client-full client nopass', 
        cwd='/etc/openvpn/easy-rsa', 
        shell=True, check=True
    )


@patch('subprocess.run', return_value=MagicMock(returncode=1))
def test_build_client_fail(mock_run):
    success = build_client('client')
    assert success is False

    mock_run.assert_called_once_with(
        './easyrsa --batch build-client-full client nopass', 
        cwd='/etc/openvpn/easy-rsa', 
        shell=True, check=True
    )


cert_content = """
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJALb2Z6Z6Z6Z6MA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
...
-----END CERTIFICATE-----
"""


@patch('builtins.open', new_callable=mock_open, read_data=cert_content)
@patch('cryptography.x509.load_pem_x509_certificate')
def test_read_client_cert_success(mock_load_cert, mock_open):
    mock_cert = MagicMock()
    mock_cert.not_valid_before_utc = datetime.now()
    mock_cert.not_valid_after_utc = datetime.now() + timedelta(days=365)
    mock_cert.subject.get_attributes_for_oid.return_value = [MagicMock(value='client_name')]
    mock_cert.issuer.get_attributes_for_oid.return_value = [MagicMock(value='CA_name')]
    mock_load_cert.return_value = mock_cert

    result = read_client_cert('client_name')
    assert result is not None
    assert result['issued_to'] == 'client_name'
    assert result['issued_by'] == 'CA_name'
    assert result['issued_on'] == mock_cert.not_valid_before_utc
    assert result['expires_on'] == mock_cert.not_valid_after_utc
    
    mock_open.assert_called_once_with('/etc/openvpn/easy-rsa/pki/issued/client_name.crt', 'rb')
    mock_load_cert.assert_called_once()


@patch('builtins.open', side_effect=FileNotFoundError)
def test_read_client_cert_file_not_found(mock_open):
    result = read_client_cert('non_existent_client')
    assert result == {}
    mock_open.assert_called_once_with('/etc/openvpn/easy-rsa/pki/issued/non_existent_client.crt', 'rb')
    

@patch('builtins.open', new_callable=mock_open, read_data='Invalid certificate content')
@patch('cryptography.x509.load_pem_x509_certificate', side_effect=ValueError('Invalid certificate'))
def test_read_client_cert_invalid_certificate(mock_load_cert, mock_open):
    result = read_client_cert('invalid_client')
    assert result == {}
    mock_open.assert_called_once_with('/etc/openvpn/easy-rsa/pki/issued/invalid_client.crt', 'rb')
    mock_load_cert.assert_called_once()


@patch('os.remove')
@patch('zipfile.ZipFile', return_value=MagicMock())
def test_package_client_cert(mock_zipfile, mock_remove):    
    package_client_cert(name='test_client', output_dir='/path/to/output_dir')
    mock_zipfile.assert_called_once_with('/path/to/output_dir/test_client.zip', 'w', zipfile.ZIP_DEFLATED)
    mock_remove.assert_called_once_with('/path/to/output_dir/test_client.zip')


@patch('sciaiot.ovpncp.utils.openvpn.read_client_cert', return_value={})
@patch('subprocess.run', return_value=MagicMock(returncode=0))
def test_renew_client_cert(mock_run, mock_read_client_cert):
    cert_details = renew_client_cert('client')
    assert cert_details == {}
    
    mock_run.assert_called_once_with(
        './easyrsa --batch revoke-renewed client', 
        cwd='/etc/openvpn/easy-rsa', 
        shell=True, check=True
    )
    mock_read_client_cert.assert_called_once_with('client')


@patch('subprocess.run', return_value=MagicMock(returncode=1))
def test_renew_client_cert_fail(mock_run):
    cert_details = renew_client_cert('client')
    assert cert_details == {}
    
    mock_run.assert_called_once_with(
        './easyrsa --batch revoke-renewed client', 
        cwd='/etc/openvpn/easy-rsa', 
        shell=True, check=True
    )


@patch('subprocess.run', return_value=MagicMock(returncode=0))
def test_revoke_client_cert(mock_run):
    result = revoke_client('test_client')
    assert result is True

    mock_run.assert_called_once_with(
        './easyrsa --batch revoke test_client', 
        cwd='/etc/openvpn/easy-rsa', 
        shell=True, check=True
    )


@patch('subprocess.run', return_value=MagicMock(returncode=1))
def test_revoke_client_cert_fail(mock_run):
    result = revoke_client('test_client')
    assert result is False

    mock_run.assert_called_once_with(
        './easyrsa --batch revoke test_client', 
        cwd='/etc/openvpn/easy-rsa', 
        shell=True, check=True
    )


@patch('subprocess.run', return_value=MagicMock(returncode=0))
def test_generate_crl(mock_run):
    success = generate_crl()
    assert success is True
    
    mock_run.assert_called_once_with(
        './easyrsa --batch gen-crl', 
        cwd='/etc/openvpn/easy-rsa',   
        shell=True, check=True
    )


@patch('subprocess.run', return_value=MagicMock(returncode=1))
def test_generate_crl_fail(mock_run):
    success = generate_crl()
    assert success is False
    
    mock_run.assert_called_once_with(
        './easyrsa --batch gen-crl', 
        cwd='/etc/openvpn/easy-rsa',   
        shell=True, check=True
    )


@patch('builtins.open', new_callable=mock_open)
def test_assign_client_ip(mock_open):
    assign_client_ip('client_1', '10.8.0.2', '255.255.255.0')

    mock_open.assert_called_with('/etc/openvpn/ccd/client_1', 'w')

    handle = mock_open()
    handle.write.assert_called_with('ifconfig-push 10.8.0.2 255.255.255.0\n')


@patch('os.path.exists', return_value=True)
@patch('os.remove')
def test_unassign_client_ip(mock_remove, mock_exists):
    unassign_client_ip('client_1')
    
    mock_exists.assert_called_with('/etc/openvpn/ccd/client_1')
    mock_remove.assert_called_with('/etc/openvpn/ccd/client_1')


@patch('builtins.open', new_callable=mock_open)
def test_add_iroute(mock_open):
    add_iroute('gateway_1', '192.168.1.0 255.255.255.0')
    
    mock_open.assert_called_with('/etc/openvpn/ccd/gateway_1', 'a')
    
    handle = mock_open()
    handle.write.assert_called_with('iroute 192.168.1.0 255.255.255.0\n')


@patch('builtins.open', new_callable=mock_open, read_data='ifconfig-push 10.8.0.2 255.255.255.0\niroute 192.168.1.0 255.255.255.0\n')
def test_remove_iroute(mock_open):
    remove_iroute('gateway_1', '192.168.1.0 255.255.255.0')
    
    mock_open.assert_called_with('/etc/openvpn/ccd/gateway_1', 'w')


@patch('builtins.open', new_callable=mock_open)
def test_push_client_routes(mock_open):
    push_client_routes('client_1', ['192.168.1.5 255.255.255.255 10.8.0.11'])
    
    mock_open.assert_called_with('/etc/openvpn/ccd/client_1', 'a')
    mock_open().write.assert_called_with('push "route 192.168.1.5 255.255.255.255 10.8.0.11"\n')


@patch('builtins.open', new_callable=mock_open, read_data='ifconfig-push 10.8.0.2 255.255.255.0\npush "route 192.168.1.5 255.255.255.255 10.8.0.11"\n')
def test_pull_client_routes(mock_open):
    pull_client_routes('client_1')
    
    mock_open.assert_called_with('/etc/openvpn/ccd/client_1', 'w')


connection_lines = """
OpenVPN CLIENT LIST
Updated,2025-01-14 06:04:39
Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
client_1,172.205.176.207:60374,3051,3093,2025-01-14 06:04:34
client_2,172.205.176.208:60374,3051,3093,2025-01-14 06:04:34
ROUTING TABLE
Virtual Address,Common Name,Real Address,Last Ref
10.8.0.2,client_1,172.205.176.207:60374,2025-01-14 06:04:35
10.8.0.3,client_2,172.205.176.208:60374,2025-01-14 06:04:35
GLOBAL STATS
Max bcast/mcast queue length,0
END
"""
connection_lines_empty = """
OpenVPN CLIENT LIST
Updated,2025-01-14 06:55:30
Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
ROUTING TABLE
Virtual Address,Common Name,Real Address,Last Ref
GLOBAL STATS
Max bcast/mcast queue length,0
END
"""


@patch('builtins.open', new_callable=mock_open, read_data=connection_lines)
def test_list_connections(mock_open):
    connections = list_connections()

    assert connections is not None
    assert len(connections) == 2
    assert connections[0] == {
        'name': 'client_1',
        'ip': '10.8.0.2',
        'remote_address': '172.205.176.207:60374',
        'connected_time': '2025-01-14 06:04:34'
    }
    assert connections[1] == {
        'name': 'client_2',
        'ip': '10.8.0.3',
        'remote_address': '172.205.176.208:60374',
        'connected_time': '2025-01-14 06:04:34'
    }

    mock_open.assert_called_with('/var/log/openvpn/openvpn-status.log', 'r')


@patch('builtins.open', new_callable=mock_open, read_data=connection_lines_empty)
def test_connection_with_empty_output(mock_open):
    connections = list_connections()

    assert connections is not None
    assert len(connections) == 0

    mock_open.assert_called_with('/var/log/openvpn/openvpn-status.log', 'r')
