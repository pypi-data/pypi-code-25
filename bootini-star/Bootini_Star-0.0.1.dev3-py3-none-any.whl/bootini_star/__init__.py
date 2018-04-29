"""
Inspect EVE Online in-game mail and skill queues in a web browser. Inspired by
CCP's discontinued EVE Gate app.

This project was started on 2018-04-20 by Ralph Seichter.
"""
__author__ = 'Ralph Seichter'

import os
import re

from flask import Flask
from flask.views import MethodView
from flask_migrate import Migrate, migrate
from flask_sqlalchemy import SQLAlchemy

from .extensions import db, login_manager
from .sso_views import blueprint as sso_blueprint
from .views import blueprint as bs_blueprint

app = Flask(__name__)
# Development configuration settings are the default.
app_settings = os.getenv('APP_SETTINGS', 'bootini_star.config.Development')
app.config.from_object(app_settings)

db.init_app(app)
migrate = Migrate(app, db)

login_manager.init_app(app)
login_manager.login_message_category = 'info'
login_manager.blueprint_login_views = {
    bs_blueprint.name: 'bs.login',
    sso_blueprint.name: 'bs.login'
}

app.register_blueprint(bs_blueprint)
app.register_blueprint(sso_blueprint)


_re_flags = re.RegexFlag.MULTILINE
_div_pat = re.compile(r'<div>(.*?)</div>', flags=_re_flags)
_font_pat = re.compile(r'<(font[^>]*|/font)>', flags=_re_flags)
_span_pat = re.compile(r'<(span[^>]*|/span)>', flags=_re_flags)
_si_pat = re.compile(r'href="showinfo:(\d+)//(\d+)"', flags=_re_flags)


@app.template_filter('eve_html')
def html_filter(html):
    """
    Strip selected HTML tags created within EVE's mail client.

    :type html: str
    :param html: HTML string to clean up
    """
    html = re.sub(_font_pat, '', html)
    html = re.sub(_span_pat, '', html)
    return re.sub(_div_pat, r'\1', html)


@app.template_filter('showinfo')
def showinfo_filter(html, urlbase):
    """
    Convert EVE 'showinfo' links into HTML links. This currently only works for
    links that reference EVE characters, other link types are ignored.

    :type html: str
    :param html: HTML string to parse.
    """
    flags = _re_flags
    pos = 0
    m = _si_pat.search(html)
    while m:
        if 1373 <= int(m.group(1)) <= 1386:
            href = 'href="%scharacter/%s"' % (urlbase, m.group(2))
            html = re.sub(m.group(0), href, html, flags=flags)
        pos += len(m.group(0))
        m = _si_pat.search(html, pos)
    return html
