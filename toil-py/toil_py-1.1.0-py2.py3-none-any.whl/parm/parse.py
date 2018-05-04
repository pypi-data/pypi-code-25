# -*- coding: utf-8 -*-
""" Handle supported framework parameters. """
import argparse
import logging

logger = logging.getLogger(__name__)


def parse_parameters(mandatory=None, optional=None):
    """Handle parameters passed to a program.

    This method handles the standard framework parameters.
      -v = verbose
      -c = config file
      -u = universal application identifier
      -o = options
      -k = encryption key
      -e = environment
      -r = regex used to determine what config items to encrypt / decrypt

    User defined parameters are allowed as well.

    Args:
      mandatory: A list of mandatory arguments.
      optional: A list of optional arguments.

    Returns:
      A dict mapping parameters to the values provided.

    Raises:
      When an error is encountered usage is printed and program exits.
    """
    standard_args = {'v', 'c', 'u', 'o', 'k', 'e'}
    parser = argparse.ArgumentParser(description='cloud python library')

    if mandatory is None:
        mandatory = []

    if optional is None:
        optional = []

    for arg in mandatory:
        if arg not in standard_args:
            parser.add_argument('-' + arg, help=arg, required=True)

    for arg in optional:
        if arg not in standard_args:
            parser.add_argument('--' + arg, help=arg, required=False)

    parser.add_argument('-c', dest='config_file', help='config file', required=('c' in mandatory))
    parser.add_argument('-v', dest='verbose', action='store_true', default=False, help='verbose output',
                        required=('v' in mandatory))
    parser.add_argument('-o', dest='options', help='declare hash for options {parm: value}',
                        required=('o' in mandatory))
    parser.add_argument('-k', dest='encryption_key', help='encryption key', required=('k' in mandatory))
    parser.add_argument('-r', dest='encrypted_config_keys_regex', default='.*',
                        help='regex pattern for keys that are encrypted in config file', required=('r' in mandatory))
    parser.add_argument('-e', dest='env', default='dev',
                        help='environment[dev,stage, preprod, prod]', required=('e' in mandatory))
    # encrypted_config_keys_regex = r'key_id|secret|password'

    args = parser.parse_args()

    # convert the returned namespace attributes to a dict.
    arg_map = vars(args)

    # set args per standard names.
    arg_map['v'] = arg_map['verbose']
    if 'config_file' in arg_map:
        arg_map['c'] = arg_map['config_file']
    if 'encryption_key' in arg_map:
        arg_map['k'] = arg_map['encryption_key']
    if 'env' in arg_map:
        arg_map['e'] = arg_map['env']

    # enable debugging for all logging
    if arg_map['verbose']:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s %(message)s', level=logging.DEBUG)
        logger.debug('verbose logging')

    # arg_map_filtered = {k: v for k, v in arg_map.iteritems() if v is not None}
    arg_map_filtered = arg_map
    logger.debug(arg_map_filtered)

    return arg_map_filtered


# alias the function
parms = parse_parameters
handle_parms = parse_parameters
handle_parameters = parse_parameters
