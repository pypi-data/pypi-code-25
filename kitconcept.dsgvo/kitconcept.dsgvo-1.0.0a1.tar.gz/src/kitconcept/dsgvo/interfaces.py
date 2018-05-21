# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.z3cform.interfaces import ISingleCheckBoxBoolWidget


class IKitconceptDsgvoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDsgvoSingleCheckBoxBoolWidget(ISingleCheckBoxBoolWidget):
    """Marker interface for the SingleCheckboxBoolWidget."""
