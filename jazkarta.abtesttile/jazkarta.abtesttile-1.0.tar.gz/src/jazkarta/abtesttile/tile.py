import logging
from lxml import etree
from plone.app.textfield import RichText
from plone.tiles import PersistentTile
from plone.supermodel import model
from zope import schema
from . import _

logger = logging.getLogger(__name__)


class IABTestTile(model.Schema):

    text_a = RichText(
        title=_(u'Text A'),
        allowed_mime_types=('text/html',),
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe',
        required=True)

    script_a = schema.Text(
        title=_(u'Script A'),
        description=_(u'Javscript code that runs when text A is displayed. '
                      u'Include tracking data here as needed. Be careful!!'),
        required=False,
    )

    text_b = RichText(
        title=_(u'Text B'),
        allowed_mime_types=('text/html',),
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe',
        required=True)

    script_b = schema.Text(
        title=_(u'Script B'),
        description=_(u'Javscript code that runs when text B is displayed. '
                      u'Include tracking data here as needed. Be careful!!'),
        required=False,
    )

    ratio = schema.Int(
        title=_(u'Percentage of time that tile A will be shown'),
        min=0,
        max=100,
        default=50,
        required=True)

    campaign_marker = schema.Bool(
        title=_(u'Add campaign marker query string to all link urls'),
        description=_(u'Adds a query string variable "ab_campaign=a-${id}" '
                     u' or "ab_campaign=b-${id}" to all urls in the html fields.'),
        default=False)


class ABTestTile(PersistentTile):
    """Existing content tile
    """

    def _add_campaign_markers(self, html, marker):
        if not html or not html.output:
            return u''

        html = html.output
        if not self.data.get('campaign_marker', False):
            return html

        try:
            root = etree.fromstring(html)
            links = root.findall('.//a')
            for link in links:
                href = link.get('href')
                if href and u'?' in href:
                    link.set('href', u'{}&ab_campaign={}'.format(href, marker))
                elif href:
                    link.set('href', u'{}?ab_campaign={}'.format(href, marker))
            html = etree.tostring(root, pretty_print=True)
        except Exception:
            logger.exception(
                'Error making html substitution for AB Tile.'
            )
        return html

    def text_a(self):
        return self._add_campaign_markers(
            self.data.get('text_a', u''),
            u'a-{}'.format(self.id)
        )

    def text_b(self):
        return self._add_campaign_markers(
            self.data.get('text_b', u''),
            u'b-{}'.format(self.id)
        )
