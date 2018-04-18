
import logging
log = logging.getLogger(__name__)

import sys, cssutils
cssutils.log.setLevel(logging.FATAL)

from bl.dict import Dict
from bl.string import String

class Styles(Dict):

    @classmethod
    def styleProperties(Class, style):
        """return a properties dict from a given cssutils style
        """
        properties = Dict()
        for property in style.getProperties(all=True):
            stylename = property.name + ':'
            properties[stylename] = property.value
            if property.priority != '':
                properties[stylename] = ' !'+property.priority
        return properties

    @classmethod
    def from_css(Class, csstext, encoding=None, href=None, media=None, title=None, validate=None):
        """parse CSS text into a Styles object, using cssutils
        """
        styles = Class()
        cssStyleSheet = cssutils.parseString(csstext, encoding=encoding, href=href, media=media, title=title, validate=validate)
        for rule in cssStyleSheet.cssRules:
            if rule.type==cssutils.css.CSSRule.FONT_FACE_RULE:
                if styles.get('@font-face') is None: styles['@font-face'] = []
                styles['@font-face'].append(Class.styleProperties(rule.style))
            
            elif rule.type==cssutils.css.CSSRule.IMPORT_RULE:
                if styles.get('@import') is None: styles['@import'] = []
                styles['@import'].append("url(%s)" % rule.href)

            elif rule.type==cssutils.css.CSSRule.NAMESPACE_RULE:
                if styles.get('@namespace') is None: styles['@namespace'] = {}
                styles['@namespace'][rule.prefix] = rule.namespaceURI
            
            elif rule.type==cssutils.css.CSSRule.MEDIA_RULE:
                if styles.get('@media') is None: styles['@media'] = []
                styles['@media'].append(rule.cssText)
            
            elif rule.type==cssutils.css.CSSRule.PAGE_RULE:
                if styles.get('@page') is None: styles['@page'] = []
                styles['@page'].append(rule.cssText)

            elif rule.type==cssutils.css.CSSRule.STYLE_RULE:
                for selector in rule.selectorList:
                    sel = selector.selectorText
                    if sel not in styles:
                        styles[sel] = Class.styleProperties(rule.style)
            
            elif rule.type==cssutils.css.CSSRule.CHARSET_RULE:
                styles['@charset'] = rule.encoding

            elif rule.type==cssutils.css.CSSRule.COMMENT:   # comments are thrown away
                pass

            elif rule.type==cssutils.css.CSSRule.VARIABLES_RULE:
                pass
            
            else:
                log.warning("Unknown rule type: %r" % rule.cssText)

        return styles
    
    @classmethod    
    def render(C, styles, margin='', indent='\t'):
        """output css text from styles. 
        margin is what to put at the beginning of every line in the output.
        indent is how much to indent indented lines (such as inside braces).
        """
        from unum import Unum
        s = ""
        # render the css text
        for k in styles.keys():
            s += margin
            if type(styles[k]) == Unum:
                s += k + ' ' + str(styles[k]) + ';'
            elif type(styles[k]) in [str, String]:
                s += k + ' ' + styles[k] + ';'
            elif type(styles[k]) in [dict, Dict]:
                # recurse
                s += k + ' {\n' + C.render(styles[k], margin=margin+indent, indent=indent) + '}\n'
            elif type(styles[k]) in [tuple, list]:
                for i in styles[k]:
                    s += k + ' ' 
                    if type(i) in [str, String]:
                        s += i + ';\n'
                    if type(i) == bytes:
                        s += str(i, 'utf-8') + ';\n'
                    elif type(i) in [dict, Dict]:
                        # recurse
                        s += '{\n' + C.render(i, margin=margin+indent, indent=indent) + '}\n'
            else:
                s += ';'
            s += '\n'
        return s

