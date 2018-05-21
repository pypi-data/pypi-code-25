import sys
from collections import OrderedDict

_module = sys.modules[__name__]
_tags = ['A', 'Abbr', 'Acronym', 'Address', 'Applet', 'Area', 'Article',
         'Aside', 'Audio', 'B', 'Base', 'Basefont', 'Bdi', 'Bdo', 'Big',
         'Blockquote', 'Body', 'Br', 'Button', 'Canvas', 'Caption', 'Center',
         'Cite', 'Code', 'Col', 'Colgroup', 'Data', 'Datalist', 'Dd', 'Del_',
         'Details', 'Dfn', 'Dialog', 'Dir', 'Div', 'Dl', 'Dt', 'Em', 'Embed',
         'Fieldset', 'Figcaption', 'Figure', 'Font', 'Footer', 'Form', 'Frame',
         'Frameset', 'H1', 'H6', 'Head', 'Header', 'Hr', 'Html', 'I', 'Iframe',
         'Img', 'Input', 'Ins', 'Kbd', 'Label', 'Legend', 'Li', 'Link', 'Main',
         'Map', 'Mark', 'Menu', 'Menuitem', 'Meta', 'Meter', 'Nav', 'Noframes',
         'Noscript', 'Object', 'Ol', 'Optgroup', 'Option', 'Output', 'P',
         'Param', 'Picture', 'Pre', 'Progress', 'Q', 'Rp', 'Rt', 'Ruby', 'S',
         'Samp', 'Script', 'Section', 'Select', 'Small', 'Source', 'Span',
         'Strike', 'Strong', 'Style', 'Sub', 'Summary', 'Sup', 'Svg', 'Table',
         'Tbody', 'Td', 'Template', 'Textarea', 'Tfoot', 'Th', 'Thead', 'Time',
         'Title', 'Tr', 'Track', 'Tt', 'U', 'Ul', 'Var', 'Video', 'Wbr',

         # lower case versions
         'a', 'abbr', 'acronym', 'address', 'applet', 'area', 'article',
         'aside', 'audio', 'b', 'base', 'basefont', 'bdi', 'bdo', 'big',
         'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'center',
         'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del_',
         'details', 'dfn', 'dialog', 'dir', 'div', 'dl', 'dt', 'em', 'embed',
         'fieldset', 'figcaption', 'figure', 'font', 'footer', 'form', 'frame',
         'frameset', 'h1', 'h6', 'head', 'header', 'hr', 'html', 'i', 'iframe',
         'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main',
         'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noframes',
         'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 'p',
         'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's',
         'samp', 'script', 'section', 'select', 'small', 'source', 'span',
         'strike', 'strong', 'style', 'sub', 'summary', 'sup', 'svg', 'table',
         'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time',
         'title', 'tr', 'track', 'tt', 'u', 'ul', 'var', 'video', 'wbr']

__all__ = ['Tag', 'doctype'] + _tags


class Attrs(OrderedDict):
    """A dictionary subclass that can print HTML attributes correctly"""

    def __str__(self):
        if not self:
            return ''
        result = ''
        for key, value in self.items():
            key = key.lstrip('_').replace('_', '-')
            result += ' {}="{}"'.format(key, value)
        return result


class Tag(object):
    """Represent a HTML tag that can be used as a Callable or in a context.

    >>> h1 = Tag('h1', some_html_attribute='test')
    >>> h1('test')
    '<h1 some-html-attribute="test">test</h1>'

    Check out :mod:`stempl.tests` for more examples.
    """

    def __init__(self, tag_name, **attrs):
        """Create a new HTML tag.

        :param tag_name: name of the tag
        :type tag_name: str
        :param attrs: HTML attributes
        """
        self.tag_name = tag_name.lower()
        self.attrs = Attrs(attrs)
        self.body = ''

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self, body=None, **attrs):
        """Render the HTML tag as string.

        :param body: body of the HTML tag
        :type body: str
        :param attrs: extra HTML attributes to render
        :return: the string representation of the HTML tag
        """
        if body:
            self.body = body
        if attrs:
            new_attrs = OrderedDict(self.attrs.copy())
            new_attrs.update(attrs)
            self.attrs = Attrs(new_attrs)
        return str(self)

    def __lshift__(self, other):
        """Append to the body of the HTML tag.

        :param other: either a callable (another tag) or a string to append
        :type other: Union[Callable, str]
        :return: the string representation of the HTML tag
        :rtype: str
        """
        if callable(other):
            self.body += other()
        else:
            self.body += other
        return str(self)

    def __str__(self):
        """Return the string representation of the HTML tag with all it's
        attributes and body"""
        return '<{name}{attrs}>{body}</{name}>'.format(
            name=self.tag_name, attrs=self.attrs, body=self.body)


def doctype():
    """DOCTYPE tag"""
    return '<!DOCTYPE html>'


def _class_wrapper(name):
    """wrapper for the class version of the tag"""
    def wrapped(**attrs):
        return Tag(name, **attrs)
    return wrapped


def _func_wrapper(name):
    """wrapper for the function version of the tag"""
    def wrapped(body=None, **attrs):
        return Tag(name, **attrs)(body)
    return wrapped


# add the wrapper functions to the module
for t in _tags:
    setattr(_module, t, _class_wrapper(t.lower()))
    setattr(_module, t.lower(), _func_wrapper(t.lower()))
