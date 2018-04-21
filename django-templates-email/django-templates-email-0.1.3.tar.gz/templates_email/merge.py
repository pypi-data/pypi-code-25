from collections import namedtuple
from django.template import TemplateDoesNotExist
from django.utils import translation
from lxml.html import document_fromstring
import os
from premailer import premailer
from render_block import render_block_to_string

from .config import default_fallback_language

MergedEmail = namedtuple('MergedEmail', 'template language subject html plain')


def merge(template_name: str, context: dict, language: str,
          fallback_language: str = default_fallback_language) -> MergedEmail:
    """
    Merges the template with the given context.
    - Tries to load a localized version of the template name, by appending -language to the filename
    - If that template cannot be found and fallback_language is enabled then we try with the fallback_language
    - The language (either 'language' or 'fallback_language') is used when rendering the template,
        which impacts formatting of numbers, dates, etc
    """

    def lookup_template_and_merge_for_language(l: str) -> MergedEmail:
        ltn = localized_template_name(template_name, l)
        with translation.override(l):
            subject = render_block_to_string(ltn, 'subject', context)
            raw_html = render_block_to_string(ltn, 'html', context)
        return MergedEmail(
            template=ltn,
            language=l,
            subject=subject.strip(),
            html=premailer.transform(raw_html),
            plain=html_to_text(raw_html),
        )

    try:
        return lookup_template_and_merge_for_language(language)
    except TemplateDoesNotExist as e:
        if fallback_language and fallback_language != language:
            return lookup_template_and_merge_for_language(fallback_language)
        else:
            raise e


def localized_template_name(template_name: str, language: str) -> str:
    filename, extension = os.path.splitext(template_name)
    return '{}-{}{}'.format(filename, language, extension)


def html_to_text(html: str) -> str:
    """
    Generates a text version from the html.
    """
    document = document_fromstring(html)
    raw_text = document.body.text_content()

    # Trim all the unnecessary spaces on the right of each line, and skip duplicate lines (mostly newlines)
    clean_lines = []
    last_line = None
    for raw_line in raw_text.splitlines():
        line = raw_line.rstrip()
        if line != last_line:
            clean_lines.append(line)
        last_line = line
    return '\n'.join(clean_lines)
