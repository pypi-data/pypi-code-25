#-*- encoding:utf-8 *-
from plone import tiles
from plone.app.uuid.utils import uuidToObject


class AdvancedStaticTile(tiles.PersistentTile):

    @property
    def portlet_class(self):
        classes = 'tile tile-advanced-static'
        cssclass = self.data.get('tile_class', None)
        cssstyle = self.data.get('css_style', '')
        if cssclass:
            classes += ' {}'.format(cssclass)
        if cssstyle:
            classes += ' {}'.format(cssstyle)
        return classes

    @property
    def image_url(self):
        image_ref = self.data.get('image_ref', None)
        if image_ref:
            obj = uuidToObject(image_ref)
            if obj:
                return obj.absolute_url()

    @property
    def image_heigth(self):
        image_ref = self.data.get('image_ref', None)
        image_ref_height = self.data.get('image_ref_height', None)
        if image_ref:
            if image_ref_height:
                return image_ref_height
            else:
                obj = uuidToObject(image_ref)
                if obj:
                    return obj.getIamge().height
                else:
                    return ''

    @property
    def img_style(self):
        style = ''
        if self.image_url:
            style += "background-image:url({})".format(self.image_url)
            if self.image_heigth:
                style += ";height:{}px".format(self.image_heigth)
            return style
        return None

    @property
    def tile_link(self):
        internal_url = self.data.get('internal_url', None)
        more_link = self.data.get('more_link', None)
        if internal_url:
            obj = uuidToObject(internal_url)
            if obj:
                return obj.absolute_url()
            else:
                return None
        elif more_link:
            return more_link
