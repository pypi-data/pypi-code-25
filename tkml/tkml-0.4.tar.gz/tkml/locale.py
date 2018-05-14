import gettext
from gettext import GNUTranslations
import os.path as path
from .helpers import get_back_frame

def use(domain: str, *, localedir: str=None,
        language: str=None) -> GNUTranslations:
    if localedir is None:
        frame = get_back_frame()
        directory = path.dirname(frame.f_code.co_filename)
        localedir = path.realpath(path.join(directory, 'locales'))
    if language is None:
        language, *_ = gettext.locale.getlocale()

    lang = gettext.translation(
        domain, localedir=localedir, languages=[language],
    )
    lang.install()
    return lang
