from os.path import exists
import shutil

from ..landing_zone import LandingZone


def create_example(development_landing_zone, reset, print_ok, print_err):
    """creates local example landing zone serving examples for the initial setup.
    """

    print_ok("- setup example landing zone")

    if exists(development_landing_zone):
        if not reset:
            print_err("  - folder {} already exists.".format(development_landing_zone))
            return 1
        else:
            try:
                shutil.rmtree(development_landing_zone)
            except Exception as e:
                print_err("  - could not delete folder {}".format(development_landing_zone))
                print_err("  - error message is: {}".format(e))
                return 1

    LandingZone.create_from_empty(development_landing_zone)

    print_ok("+ example landing zone created", fg="green")
    return 0
