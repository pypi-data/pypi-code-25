"""
aggiestack

Usage:
  aggiestack server create [--image=<IMAGE> --flavor=<FLAVOR_NAME>] <INSTANCE_NAME>
  aggiestack server delete <INSTANCE_NAME>
  aggiestack server list
  aggiestack admin show hardware 
  aggiestack admin show instances
  aggiestack admin can_host <MACHINE_NAME> <FLAVOR>
  aggiestack admin show imagecaches <RACK_NAME>
  aggiestack admin evacuate <RACK_NAME>
  aggiestack admin remove <MACHINE>
  aggiestack admin clear_all
  aggiestack admin add -mem MEM -disk NUM_DISKS -vcpus VCPU -ip IP -rack RACK_NAME MACHINE
  aggiestack show hardware
  aggiestack show images
  aggiestack show flavors 
  aggiestack show all 
  aggiestack show logs 
  aggiestack config [--images=<IMAGES_PATH> | --flavors=<FLAVORS_PATH> | --hardware=<HARDWARE_PATH> ] 
  aggiestack config load <CONGFIG_PATH>  
  aggiestack -h | --help
  aggiestack --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  aggiestack admin show hardware

Help:
  For help using this tool, please open an issue on the Github repository:

"""

from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION

import json

from utils import logger


def main():
    """Main CLI entrypoint."""
    import aggiestack.commands
    options = docopt(__doc__, version=VERSION)

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    for (k, v) in options.items(): 
        if hasattr(aggiestack.commands, k) and v:
            module = getattr(aggiestack.commands, k)
            if module.__name__ != 'aggiestack.commands.admin':
              aggiestack.commands = getmembers(module, isclass)
              command = [command[1] for command in aggiestack.commands if command[0] != 'Base'][0]
              command = command(options)
              command.run()
            else:                                     #Workaround for admin reserved keyword
              aa = module.AlterAdmin(options)
              aa.run()

            logoptions = {k: v for k, v in options.items() if v}
            logger.log(json.dumps(logoptions), False,True)
            
         


  # aggiestack server create [--image=<IMAGE> --flavor=<FLAVOR_NAME>] <INSTANCE_NAME>                   --done
  # aggiestack server delete <INSTANCE_NAME>                                                            --done
  # aggiestack server list                                                                              --done
  # aggiestack admin show hardware                                                                      --done
  # aggiestack admin show instances                                                                     --done
  # aggiestack admin can_host <MACHINE_NAME> <FLAVOR>
  # aggiestack admin show imagecaches <RACK_NAME>
  # aggiestack admin evacuate <RACK_NAME>
  # aggiestack admin remove   <MACHINE>
  # aggiestack admin add -mem MEM -disk NUM_DISKS -vcpus VCPU -ip IP -rack RACK_NAME MACHINE            --done    
  # aggiestack show                                                                                     --done
  # aggiestack show images                                                                              --done
  # aggiestack show flavors                                                                             --done
  # aggiestack show all                                                                                 --done
  # aggiestack show logs                                                                                --done
  # aggiestack config [--images=<IMAGES_PATH> | --flavors=<FLAVORS_PATH> | --hardware=<HARDWARE_PATH> ] -- done
  # aggiestack config load <CONGFIG_PATH>  
  # aggiestack -h | --help                                                                               --done
  # aggiestack --version                                                                                 --done

