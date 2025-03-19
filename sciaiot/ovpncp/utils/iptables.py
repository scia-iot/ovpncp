import logging
import subprocess

logger = logging.getLogger(__name__)


def list_rules(chain):
    '''
    List iptables rules for a specified chain with line numbers.

    :param chain: The name of the chain (e.g., 'INPUT', 'OUTPUT', 'FORWARD', 'PREROUTING', 'POSTROUTING')
    :return: A list of strings, each representing a rule with its line number
    '''

    logging.info(f'Listing iptables rules for chain: {chain}')
    # Execute the iptables command with the --line-numbers and --list options
    result = subprocess.run(
        ['iptables', '-L', chain, '--line-numbers'],
        capture_output=True,
        text=True,
        check=True
    )

    # Split the output into lines
    lines = result.stdout.splitlines()
    # Skip the first two lines (chain name and header)
    rules = lines[2:]
    logging.info('Successfully listed iptables rules.')

    return rules


def apply_rules(chain, line_number, rules):
    '''
    Insert multiple iptables rules before a specified line number in the given chain.

    :param chain: The name of the chain (e.g., 'INPUT', 'OUTPUT', 'FORWARD', 'PREROUTING', 'POSTROUTING')
    :param line_number: The line number before which to insert the new rules
    :param rules: A list of iptables rules to insert (e.g., ['-p tcp --dport 80 -j ACCEPT', '-p udp --dport 53 -j ACCEPT'])
    '''

    # Construct a single shell command to insert all rules
    commands = []
    for rule in rules:
        commands.append(f'iptables -I {chain} {line_number} {rule}')
        line_number += 1
    shell_command = ' && '.join(commands)

    logging.info(
        f'Inserting iptables rules before line {line_number} in chain {chain}: {shell_command}')
    subprocess.run(shell_command, shell=True, check=True)
    logging.info(
        f'Successfully inserted all iptables rules before line {line_number}.')


def drop_rules(chain, rules):
    '''
    Drop multiple iptables rules in the given chain.
    :param chain: The name of the chain (e.g., 'INPUT', 'OUTPUT', 'FORWARD', 'PREROUTING', 'POSTROUTING')
    :param rules: A list of iptables rules to drop (e.g., ['-p tcp --dport 80 -j DROP', '-p udp --dport 53 -j DROP'])
    '''

    # Construct a single shell command to drop all rules
    commands = []
    for rule in rules:
        commands.append(f'iptables -D {chain} {rule}')
    shell_command = ' && '.join(commands)

    logging.info(f'Dropping iptables rules in chain {chain}: {shell_command}')
    subprocess.run(shell_command, shell=True, check=True)
    logging.info(f'Successfully dropped all iptables rules in chain {chain}.')
