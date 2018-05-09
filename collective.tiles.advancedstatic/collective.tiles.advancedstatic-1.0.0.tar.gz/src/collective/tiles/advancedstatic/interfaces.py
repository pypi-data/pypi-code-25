# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.supermodel import model
from zope import schema
from plone.app.textfield import RichText
from collective.tiles.advancedstatic import _
from plone.app.vocabularies.catalog import CatalogSource


class ICollectiveTilesAdvancedstaticLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAdvancedStaticTile(model.Schema):
    title = schema.TextLine(
        title=_('label_tile_title', u'Tile title'),
        required=True
    )
    footer = schema.TextLine(
        title=_('label_tile_footer', u'Tile footer'),
        required=False
    )
    text = RichText(
        title=_('label_tile_text', u'Tile text'),
        description=_('help_tile_text', u'Insert some formatted text'),
        required=False
    )
    more_link = schema.ASCIILine(
        title=_('label_tile_morelink', u'More link'),
        description=_('help_tile_morelink',
                      u'If given, the header and footer will link to this URL'),
        required=False
    )
    internal_url = schema.Choice(
        title=_('label_internal_url', u"Internal link"),
        description=_('help_internal_url',
                      u'Insert an internal link. This field override external '
                      'link field'),
        required=False,
        source=CatalogSource()
    )
    target_attr = schema.Bool(
        title=_('label_target_attr', u'Open links in a new window'),
        description=_('help_target_attr',
                      u'Tick this box if you want to open '
                      'the header and footer links in a new window'),
        required=False,
        default=False
    )
    image_ref = schema.Choice(
        title=_('label_image_ref', u'Background image'),
        description=_('help_image_ref',
                      u'Insert an image that will be shown as background of '
                      'the header'),
        required=False,
        source=CatalogSource(portal_type=('Image'))
    )
    image_ref_height = schema.Int(
        title=_('label_image_ref_height', u'Background image height'),
        description=_('help_image_ref_height',
                      u'Specify image background\'s height (in pixels). '
                      'If empty will be used image\'s height.'),
        required=False
    )
    tile_class = schema.TextLine(
        title=_('label_tile_class', u'tile class'),
        required=False,
        description=_('help_tile_class', u'CSS class to add at the tile')
    )
    css_style = schema.Choice(
        title=_('label_tile_style', u'Portlet style'),
        description=_('help_tile_style', u'Choose a CSS style for the tile'),
        required=False,
        vocabulary='collective.tiles.advancedstatic.CSSVocabulary'
    )
