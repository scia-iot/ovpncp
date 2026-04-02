from unittest.mock import MagicMock, patch, call
import pytest
from sciaiot.ovpncp.utils.iptables import apply_rules, drop_rules, list_rules

rules_output = """Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
 1    100 DROP       all  --  tun0   *       0.0.0.0/0            0.0.0.0/0
"""


@patch("subprocess.run")
def test_list_rules(mock_run):
    mock_run.return_value = MagicMock(stdout=rules_output)

    result = list_rules("FORWARD")
    expected_output = [
        " 1    100 DROP       all  --  tun0   *       0.0.0.0/0            0.0.0.0/0"
    ]
    assert result == expected_output

    mock_run.assert_called_once_with(
        ["iptables", "-L", "FORWARD", "--line-numbers"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_apply_rules_injection(mock_run):
    malicious_rule = "-j ACCEPT; touch /tmp/iptables_injected"
    with pytest.raises(ValueError, match="Malicious characters"):
        apply_rules("FORWARD", 1, [malicious_rule])

    mock_run.assert_not_called()


@patch("subprocess.run")
def test_apply_rules(mock_run):
    rules = [
        "-i tun0 -s 10.8.0.2 -d 10.8.0.3 -j ACCEPT",
        "-i tun0 -s 10.8.0.3 -d 10.8.0.3 -j ACCEPT",
    ]

    apply_rules("FORWARD", 1, rules)

    assert mock_run.call_count == 2
    mock_run.assert_has_calls(
        [
            call(
                [
                    "iptables",
                    "-I",
                    "FORWARD",
                    "1",
                    "-i",
                    "tun0",
                    "-s",
                    "10.8.0.2",
                    "-d",
                    "10.8.0.3",
                    "-j",
                    "ACCEPT",
                ],
                shell=False,
                check=True,
            ),
            call(
                [
                    "iptables",
                    "-I",
                    "FORWARD",
                    "2",
                    "-i",
                    "tun0",
                    "-s",
                    "10.8.0.3",
                    "-d",
                    "10.8.0.3",
                    "-j",
                    "ACCEPT",
                ],
                shell=False,
                check=True,
            ),
        ]
    )


@patch("subprocess.run")
def test_drop_rules(mock_run):
    rules = [
        "-i tun0 -s 10.8.0.2 -d 10.8.0.3 -j ACCEPT",
        "-i tun0 -s 10.8.0.3 -d 10.8.0.3 -j ACCEPT",
    ]

    drop_rules("FORWARD", rules)

    assert mock_run.call_count == 2
    mock_run.assert_has_calls(
        [
            call(
                [
                    "iptables",
                    "-D",
                    "FORWARD",
                    "-i",
                    "tun0",
                    "-s",
                    "10.8.0.2",
                    "-d",
                    "10.8.0.3",
                    "-j",
                    "ACCEPT",
                ],
                shell=False,
                check=True,
            ),
            call(
                [
                    "iptables",
                    "-D",
                    "FORWARD",
                    "-i",
                    "tun0",
                    "-s",
                    "10.8.0.3",
                    "-d",
                    "10.8.0.3",
                    "-j",
                    "ACCEPT",
                ],
                shell=False,
                check=True,
            ),
        ]
    )


def test_validate_chain():
    from sciaiot.ovpncp.utils.iptables import validate_chain

    validate_chain("FORWARD")
    with pytest.raises(ValueError, match="Invalid chain"):
        validate_chain("INVALID_CHAIN")
