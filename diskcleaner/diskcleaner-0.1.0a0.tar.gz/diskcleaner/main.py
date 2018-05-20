import argparse
import logging

from .cleaner import clean_directories, validate_same_volume

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--percentage', default=90,
        type=float,
        help='Percentage to try to keep volume below. Default is 90.'
    )
    parser.add_argument(
        'directories', nargs='+',
        help='Directories to cleanup.'
    )
    parser.add_argument(
        '-i', '--include', nargs='+',
        help='Regexes to include.',
        default=[]
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Extra logging.'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    percentage = args.percentage
    directories = args.directories
    verbose = args.verbose
    include = args.include

    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format=log_fmt)
    else:
        logging.basicConfig(format=log_fmt)

    if not validate_same_volume(directories):
        logger.error('Directories provided don\'t come from the same volume.')
        return 1
    else:
        ret = clean_directories(
            directories, percentage, include=include
        )
        if not ret:
            logger.error('Could not clear volume sufficiently.')
            return 1
    return 0
