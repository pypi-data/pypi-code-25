# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from xml.parsers.expat import ExpatError

import six
import xmltodict
from pywe_utils import to_text


__all__ = ['dict_to_xml', 'xml_to_dict', 'pair_to_xml']


def dict_to_xml(d, ignore=True, isdigit=True, subxml=False):
    # If subxml, add '<xml>\n'
    xml = [] if subxml else ['<xml>\n']
    # Foreach joint kv
    for k, v in d.items():
        if (ignore and v) or (not ignore):
            # If ``v`` is dict.
            # Loop call dict_to_xml
            if isinstance(v, dict):
                xml.append('<{0}>\n{1}</{0}>\n'.format(to_text(k), dict_to_xml(v, subxml=True)))
            elif isinstance(v, six.integer_types) or (isdigit and v.isdigit()):
                xml.append('<{0}>{1}</{0}>\n'.format(to_text(k), to_text(v)))
            else:
                xml.append('<{0}><![CDATA[{1}]]></{0}>\n'.format(to_text(k), to_text(v)))
    # If subxml, add '</xml>'
    if not subxml:
        xml.append('</xml>')
    return ''.join(xml)


def xml_to_dict(x):
    try:
        return xmltodict.parse(x)['xml']
    except (xmltodict.ParsingInterrupted, ExpatError):
        return x


def pair_to_xml(listuple, ignore=True, isdigit=True, subxml=False):
    """
    [('a', 1), ('b', 2), ('c', [('d', 4)])...]
    [('a', 1), ('b', 2), ('c', [[('d', 4)], [('e', 5)]])...]
    """
    # If subxml, add '<xml>\n'
    xml = [] if subxml else ['<xml>\n']
    # Foreach joint kv
    try:
        for k, v in listuple:
            if (ignore and v) or (not ignore):
                # If ``v`` is dict.
                # Loop call dict_to_xml
                if isinstance(v, list):
                    xml.append('<{0}>\n{1}</{0}>\n'.format(to_text(k), pair_to_xml(v, subxml=True)))
                elif isinstance(v, six.integer_types) or (isdigit and v.isdigit()):
                    xml.append('<{0}>{1}</{0}>\n'.format(to_text(k), to_text(v)))
                else:
                    xml.append('<{0}><![CDATA[{1}]]></{0}>\n'.format(to_text(k), to_text(v)))
    except ValueError:
        for ltup in listuple:
            xml.append('<item>\n{0}</item>\n'.format(pair_to_xml(ltup, subxml=True)))
    # If subxml, add '</xml>'
    if not subxml:
        xml.append('</xml>')
    return ''.join(xml)
