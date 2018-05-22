# -*- coding: utf-8 -*-
"""Propertyshelf MLS Plone Embedding."""

from plone import api as ploneapi
from ps.plone.mls import config
from zope.i18nmessageid import MessageFactory

import logging


PLONE_4 = '4' <= ploneapi.env.plone_version() < '5'
PLONE_5 = '5' <= ploneapi.env.plone_version() < '6'

logger = logging.getLogger(config.PROJECT_NAME)
_ = MessageFactory('ps.plone.mls')
