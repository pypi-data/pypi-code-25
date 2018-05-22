# -*- coding: utf-8 -*-
"""Usage overview control panel."""

from plone import api
from plone.mls.core.interfaces import ILocalMLSSettings
from plone.mls.listing.browser.listing_collection import IListingCollection
from plone.mls.listing.browser.listing_search import IListingSearch
from plone.mls.listing.browser.recent_listings import IRecentListings
from plone.mls.listing.interfaces import ILocalAgencyInfo
from Products.Five.browser import BrowserView
from ps.plone.mls.browser.listings.featured import IFeaturedListings
from ps.plone.mls.interfaces import IDevelopmentCollection
from ps.plone.mls.interfaces import IListingSearchBanner


class UsageControlPanel(BrowserView):
    """MLS Embedding Usage overview control panel."""

    def get_listing_collections(self):
        """Get all activated listing collections."""
        return api.content.find(
            object_provides=IListingCollection,
            sort_on='sortable_title',
        )

    def get_listing_searches(self):
        """Get all activated listing searches."""
        return api.content.find(
            object_provides=IListingSearch,
            sort_on='sortable_title',
        )

    def get_listing_search_banners(self):
        """Get all activated listing search banners."""
        return api.content.find(
            object_provides=IListingSearchBanner,
            sort_on='sortable_title',
        )

    def get_recent_listings(self):
        """Get all activated recent listings."""
        return api.content.find(
            object_provides=IRecentListings,
            sort_on='sortable_title',
        )

    def get_featured_listings(self):
        """Get all activated featured listings."""
        return api.content.find(
            object_provides=IFeaturedListings,
            sort_on='sortable_title',
        )

    def get_development_collections(self):
        """Get all activated development collections."""
        return api.content.find(
            object_provides=IDevelopmentCollection,
            sort_on='sortable_title',
        )

    def get_local_mls_settings(self):
        """Get all activated local MLS settings."""
        return api.content.find(
            object_provides=ILocalMLSSettings,
            sort_on='sortable_title',
        )

    def get_local_contact_infos(self):
        """Get all activated local contact infos."""
        return api.content.find(
            object_provides=ILocalAgencyInfo,
            sort_on='sortable_title',
        )
