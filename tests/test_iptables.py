from unittest.mock import MagicMock, patch

from sciaiot.ovpncp.utils.iptables import apply_rules, drop_rules, list_rules

rules = """Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
 1    100 DROP       all  --  tun0   *       0.0.0.0/0            0.0.0.0/0
"""


@patch('subprocess.run')
def test_list_rules(mock_run):
    mock_run.return_value = MagicMock(stdout=rules)

    result = list_rules('FORWARD')
    expected_output = [
        ' 1    100 DROP       all  --  tun0   *       0.0.0.0/0            0.0.0.0/0']
    assert result == expected_output

    mock_run.assert_called_once_with(
        ['iptables', '-L', 'FORWARD', '--line-numbers'], capture_output=True, text=True, check=True)


@patch('subprocess.run')
def test_apply_rules(mock_run):
    rules = ['-i tun0 -s 10.8.0.2 -d 10.8.0.3 -j ACCEPT',
             '-i tun0 -s 10.8.0.3 -d 10.8.0.3 -j ACCEPT']
    shell_command = 'iptables -I FORWARD 1 -i tun0 -s 10.8.0.2 -d 10.8.0.3 -j ACCEPT && iptables -I FORWARD 2 -i tun0 -s 10.8.0.3 -d 10.8.0.3 -j ACCEPT'

    apply_rules('FORWARD', 1, rules)

    mock_run.assert_called_once_with(shell_command, shell=True, check=True)


@patch('subprocess.run')
def test_drop_rules(mock_run):
    rules = ['-i tun0 -s 10.8.0.2 -d 10.8.0.3 -j ACCEPT',
             '-i tun0 -s 10.8.0.3 -d 10.8.0.3 -j ACCEPT']
    shell_command = 'iptables -D FORWARD -i tun0 -s 10.8.0.2 -d 10.8.0.3 -j ACCEPT && iptables -D FORWARD -i tun0 -s 10.8.0.3 -d 10.8.0.3 -j ACCEPT'

    drop_rules('FORWARD', rules)

    mock_run.assert_called_once_with(shell_command, shell=True, check=True)
