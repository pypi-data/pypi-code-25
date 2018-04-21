"""
    AWS EC2 Volumes Check
"""

import json
import subprocess
from colors import bcolors


def get_json(command):
    """[Runs a system command with the input and returns the result in json]

    Arguments:
        command {[list]} -- [An array of string with each being a component of a command]

    Returns:
        [dict] -- [A dictionary with the returned json data]
    """

    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = process.stdout.read()
    return json.loads(output)


def print_results(data):
    """[Pretty prints an input dict]

    Arguments:
        data {[dict]} -- [input data to be printy printed]
    """

    print(json.dumps(data, indent=4))


def get_regions(regions_json_data):
    """[Function that parses the results from the regions data]

    Arguments:
        regions_json_data {[dict]} -- [The results of the aws describe regions command]

    Returns:
        [list] -- [A list of strings representing the region names]
    """

    regions = []

    for region_object in regions_json_data['Regions']:
        regions.append(region_object['RegionName'])

    return regions


def get_ec2_volumes(regions):
    """[Iterates through each AWS region and retrieves the volumes]

    Arguments:
        regions {[list]} -- [List of AWS regions as strings]

    Returns:
        [list] -- [List of volumes with each being a dict]
    """

    volumes = []

    for region in regions:
        volumes_in_region = get_json(
            ['aws', 'ec2', 'describe-volumes', '--region', region])
        for volume in volumes_in_region['Volumes']:
            volumes.append(volume)

    return volumes


def check_volume_encryption(volumes):
    """[Checks if an AWS EC2 volume is encrypted or not]

    Arguments:
        volumes {[list]} -- [A list of EC2 volumes corresponding to a particular region]
    """

    unencrypted_volumes = []

    for volume in volumes:
        if not volume['Encrypted']:
            unencrypted_volumes.append(volume)

    print('--------------------------------------------------------------------')

    for volume in unencrypted_volumes:
        print('  *  :  ' + bcolors.FAIL +
              "Volume with ID {0} is not encrypted!".format(volume['VolumeId']) + bcolors.ENDC)

    print('--------------------------------------------------------------------')


def main():
    """[Driver function that begins the script]
    """

    print("\n\nAWS EC2 Volume Encryption Check\n")

    regions = get_regions(get_json(['aws', 'ec2', 'describe-regions']))
    ec2_volumes = get_ec2_volumes(regions)
    check_volume_encryption(ec2_volumes)


main()
