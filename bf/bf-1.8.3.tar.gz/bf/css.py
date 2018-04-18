
import logging
log = logging.getLogger(__name__)

import os, re, shutil
import cssselect, cssutils
from unum import Unum       # pip install unum
from bl.file import File
from bl.url import URL
from .styles import Styles

Unum.UNIT_FORMAT = "%s"
Unum.UNIT_INDENT = ""
Unum.VALUE_FORMAT = "%s"

class CSS(File):
    """
    CSS.styles: the style rules are keys in the "styles" dict. This is limiting, but it works --  
        it happens to result in things being ordered correctly (with @-rules first), and 
        it allows us to effectively query and manipulate the contents of the stylesheet at any time.
    CSS.pt, CSS.px, CSS.em, CSS.en, CSS.inch, CSS.pi, CSS.percent: 
        All the main units are supported and are defined in terms of points, with 1.0em = 12.0pt
    """
    pt = Unum.unit('pt')
    px = Unum.unit('px', 1.0*pt)
    em = Unum.unit('em', 12.*pt)        # but em is variable to the font-size of the context.
    rem = Unum.unit('rem', 12.*pt)
    en = Unum.unit('en', 6.*pt)
    ex = Unum.unit('ex', 1.*en)
    inch = Unum.unit('in', 72.*pt)
    pi = Unum.unit('pi', 12.*pt)
    percent = Unum.unit('%', 0.01*em)

    units = {'pt':pt, 'px':px, 'em':em, 'rem':rem,'ex':ex,'in':inch,'pi':pi,'%':percent}

    def __init__(self, fn=None, styles=None, text=None, encoding='UTF-8', **args):
        File.__init__(self, fn=fn, encoding=encoding, **args)
        if styles is not None:
            self.styles = styles
        elif text is not None:
            self.styles = Styles.from_css(text)
        elif fn is not None and os.path.exists(fn):
            self.styles = Styles.from_css(open(fn, 'rb').read().decode(encoding))
        else:
            self.styles = Styles()

    @property
    def text(self):
        return self.render_styles()

    def render_styles(self, margin='', indent='\t'):
        return Styles.render(self.styles, margin=margin, indent=indent)

    def write(self, fn=None, encoding='UTF-8', **args):
        text = self.render_styles()
        File.write(self, fn=fn, data=text.encode(encoding))

    @classmethod
    def merge_stylesheets(Class, fn, *cssfns):
        """merge the given CSS files, in order, into a single stylesheet. First listed takes priority.
        """
        stylesheet = Class(fn=fn)
        for cssfn in cssfns:
            css = Class(fn=cssfn)
            for sel in sorted(css.styles.keys()):
                if sel not in stylesheet.styles:
                    stylesheet.styles[sel] = css.styles[sel]
                else: 
                    for prop in [prop for prop in css.styles[sel] if prop not in stylesheet.styles[sel]]:
                        stylesheet.styles[sel][prop] = css.styles[sel][prop]
        return stylesheet

    @classmethod
    def all_selectors(Class, fn):
        """return a sorted list of selectors that occur in the stylesheet"""
        selectors = []
        cssparser = cssutils.CSSParser(validate=False)
        css = cssparser.parseFile(fn)
        for rule in [r for r in css.cssRules if type(r)==cssutils.css.CSSStyleRule]:
            selectors += [sel.selectorText for sel in rule.selectorList]
        selectors = sorted(list(set(selectors)))
        return selectors

    @classmethod
    def selector_to_xpath(cls, selector, xmlns=None):
        """convert a css selector into an xpath expression. 
            xmlns is option single-item dict with namespace prefix and href
        """
        selector = selector.replace(' .', ' *.')
        if selector[0] == '.':
            selector = '*' + selector
            log.debug(selector)
        
        if '#' in selector:
            selector = selector.replace('#', '*#')
            log.debug(selector)

        if xmlns is not None:
            prefix = list(xmlns.keys())[0]
            href = xmlns[prefix]
            selector = ' '.join([
                (n.strip() != '>' and prefix + '|' + n.strip() or n.strip())
                for n in selector.split(' ')
                ])
            log.debug(selector)
        
        path = cssselect.GenericTranslator().css_to_xpath(selector)
        path = path.replace("descendant-or-self::", "")
        path = path.replace("/descendant::", "//")
        path = path.replace('/*/', '//')
        
        log.debug(' ==> %s' % path)
        
        return path

    @classmethod
    def cmyk_to_rgb(Class, c, m, y, k):
        """CMYK in % to RGB in 0-255
        based on https://www.openprocessing.org/sketch/46231#
        """
        c = float(c)/100.0
        m = float(m)/100.0
        y = float(y)/100.0
        k = float(k)/100.0

        nc = (c * (1-k)) + k
        nm = (m * (1-k)) + k
        ny = (y * (1-k)) + k

        r = int((1-nc) * 255)
        g = int((1-nm) * 255)
        b = int((1-ny) * 255)

        return dict(r=r, g=g, b=b)

    @classmethod
    def rgb_to_hex(Class, r, g, b):
        """RGB in 0-255 to hex (RRGGBB)"""
        return ("%2s%2s%2s" % 
                (hex(int(r)).lstrip('0x'), hex(int(g)).lstrip('0x'), hex(int(b)).lstrip('0x'))
            ).replace(' ', '0').upper()
