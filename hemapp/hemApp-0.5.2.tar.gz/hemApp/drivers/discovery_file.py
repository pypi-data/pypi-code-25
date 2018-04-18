""" Discovery of host lists from DNS e.g. Round robin hosts"""
import time
import logging
import yaml

logger = logging.getLogger(name=__name__)


def hosts(**kwargs):
    """ return hosts from file """
    results = []
    starttime = time.time()
    try:
        with open(kwargs['name'], 'rt') as source_file:
            hosts = yaml.safe_load(source_file)
            for host in hosts:
                results.append(host)
    except FileNotFoundError:
        logger.error("File not found")
    elapsed = time.time() - starttime
    logger.info("Lookup from {} took {}".format(kwargs['name'], elapsed))
    if 'metrics' in kwargs and None != kwargs['metrics']:
        kwargs['metrics'].stage(
            'discovery_file.{}.time'.format(kwargs['name'].replace('.','_')), 
            elapsed)
    return results
