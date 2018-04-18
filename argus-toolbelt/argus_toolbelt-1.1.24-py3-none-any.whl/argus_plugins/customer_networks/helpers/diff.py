from typing import List, Dict

from argus_cli.helpers import formatting

def diff_table(network_list: List) -> List[Dict[str, str]]:
    """Creates a dict with each network appearing twice, first
    with the existing data, in red, then with the changed data, 
    in green, to show the diff before creating / updating / destroying
    
    :param list network_list: List of CustomerNetworks
    :returns: List with two rows for each network, one in green and one in red
    """

    data = []
    for network in network_list:
        json = network.to_json()
        # Clean (before change) fields:
        data.append({
            "IP": formatting.red("- " + json['networkAddress']),
            "Description": formatting.red(network['description']),
            "Zone": formatting.red(network['zone'] if 'zone' in network else ''),
            "Location": formatting.red(network['location'] if 'location' in network else ''),
            "Flags": formatting.red(", ".join(network['flags']))
        })

        json.update(network._dirty)
        # Changed fields:
        data.append({
            "IP": formatting.green("+ " + json['networkAddress']),
            "Description": formatting.green(json['description']),
            "Zone": formatting.green(network['zone'] if 'zone' in network else ''),
            "Location": formatting.green(network['location'] if 'location' in network else ''),
            "Flags": formatting.green(", ".join(network.expected_flags()))
        })
    return data


def diff_file_vs_argus(
        network_list: List['CustomerNetwork'],
        existing_networks: List['CustomerNetwork'],
    ) -> Dict[str, list]:
    """Compares a list of networks from a file to the networks on Argus for the customer,
    and returns a dict with keys: NOT_IN_FILE, CHANGED_IN_FILE, NOT_ON_SERVER, UNMODIFIED

    :param list network_list: Networks in file
    :param list existing_networks: Networks on Argus
    :param str api_key: API key to perform requests with
    :return:
    """
    return {
        # Check all existing networks
        'NOT_IN_FILE': [
            network
            for network in existing_networks
            
            # Only extract the networks found on server that 
            # did not exist in the file. This allows us to delete
            # them if the user is running with deleteMissing
            if all((
                network not in network_on_file
                for network_on_file in network_list
            ))
        ],
        'CHANGED_IN_FILE': [
            # Merge networks with their server-side counter part
            # if the networks existed on Argus already
            network.merge(
                # Get the first network that is the same, but has 
                # changed locally - that is, the network address and
                # subnet matches but flags, description, or 
                # something else is different in the data received
                # from file
                next(
                    filter(
                      lambda network_on_server: (
                        network in network_on_server and
                        network != network_on_server
                      ),
                      existing_networks
                    )
                )
            )
            for network in network_list
            if any((
                network_on_server.merge(network)
                for network_on_server in existing_networks
                if network in network_on_server and network != network_on_server
            ))
        ],
        'NOT_ON_SERVER': [
            # Get networks that existed in the file but for which
            # we couldn't find any matching networks on Argus
            network
            for network in network_list
            if all((
                network not in network_on_server
                for network_on_server in existing_networks
            ))
        ],
        'UNMODIFIED': [
            # Find networks on Argus that are identical in the file
            network
            for network in network_list
            if any((
                network == network_on_server
                for network_on_server in existing_networks
            ))
        ]
    }