import gettext
from gettext import locale

def set_locale(value: str=''):
    locale.setlocale(locale.LC_ALL, value)

def bind_domain(domain: str, locales_path: str):
    gettext.bindtextdomain(domain, locales_path)
    gettext.textdomain(domain)
