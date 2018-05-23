import click
import os
import json
from colored import fg
from colored import stylize


@click.command(name='login')
def login():
    """
    args: none |
    Allows host to login on machine to be hosted

    """
    try:
        # Path to .vectordash directory
        dot_folder = os.path.expanduser('~/.vectordash/')

        # If the .vectordash directory does not exist, create it
        if not os.path.isdir(dot_folder):
            os.mkdir(dot_folder)

        # Save ids to gpu_ids file
        login_file = dot_folder + 'login.json'

        # Ask user for their machine key
        print(stylize("Machine key: ", fg("blue")))
        machine_key = input()

        # Securely save data
        with open(login_file, 'w') as f:
            data = {'machine_key': machine_key}
            json.dump(data, f)

        print(stylize("Saved login information", fg("green")))
        print("If you have already ran " + stylize("vdhost install", fg("blue")) +
              " successfully, you can now list your machine on Vectordash by running " +
              stylize("vdhost launch", fg("blue")))

    except Exception as e:
        print(stylize("The following error was encountered: ", fg("red")) + str(e))
