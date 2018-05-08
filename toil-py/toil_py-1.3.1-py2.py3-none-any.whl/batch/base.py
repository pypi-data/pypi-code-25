# -*- coding: utf-8 -*-
"""
Provides base functionality for job.
"""
import abc
import logging
import toil.framework
import toil.parm.parse

logger = logging.getLogger(__name__)


class BaseBatch(object):
    """
    Base class to provide common job behavior.

    Properties :
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        logger.debug("init")

    def run(self):
        toil_instance = self.create_toil()
        self.execute(toil_instance)
        logger.info('job finished')

    def create_toil(self):
        # require a config file to be passed in as parameter
        args = toil.parm.parse.handle_parms(['c'])

        # require config file, encyyption key and initialization vector
        # args = parm.handle.handle_parms(['c', 'k', 'i'])

        logger.debug(args)
        return toil.framework.create(**args)

    @abc.abstractmethod
    def execute(self, toil):
        return NotImplemented
