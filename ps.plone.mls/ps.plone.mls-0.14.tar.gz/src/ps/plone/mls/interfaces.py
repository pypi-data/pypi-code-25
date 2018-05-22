# -*- coding: utf-8 -*-
"""Interface definitions."""

from plone.directives import form
from plone.mls.core.interfaces import IMLSSettings as IMLSBaseSettings
from plone.mls.listing import interfaces
from ps.plone.mls import _
from zope import schema
from zope.interface import Interface


assert(IMLSBaseSettings)
IGlobalContactSettingsForm = interfaces.IMLSAgencyContactInfoSettingsEditForm
IMLSContactInfoSettings = interfaces.IMLSAgencyContactInformation
IMLSUISettings = interfaces.IMLSUISettings


class IListingTraversable(Interface):
    """Marker interface for traversable listings."""


class IDevelopmentTraversable(Interface):
    """Marker interface for traversable listings."""


class IBaseDevelopmentItems(IDevelopmentTraversable):
    """Marker interface for all development 'collection' items."""


class IDevelopmentCollection(IBaseDevelopmentItems):
    """Marker interface for DevelopmentCollection viewlet."""


class IDevelopmentDetails(Interface):
    """Marker interface for DevelopmentDetails view."""


class IDevelopmentListings(Interface):
    """Marker interface for DevelopmentListings view."""


class IPossibleDevelopmentCollection(Interface):
    """Marker interface for possible DevelopmentCollection viewlet."""


class IPossibleListingSearchBanner(Interface):
    """Marker interface for possible Listing Search Banner viewlet."""


class IListingSearchBanner(Interface):
    """Marker interface for Listing Search Banner viewlet."""


class IMLSCachingSettings(form.Schema):
    """MLS Caching Settings Schema."""

    timeout = schema.Int(
        default=3600,
        description=_(
            u'Enter the maximum time, in full seconds, that items may remain '
            u'in the cache before being requested again from the MLS. '
            u'A minimum of 60 seconds is required, a good value is 3,600 '
            u'seconds (1 hour).',
        ),
        min=60,
        required=True,
        title=_(u'Maximum age of entries in the cache'),
    )
