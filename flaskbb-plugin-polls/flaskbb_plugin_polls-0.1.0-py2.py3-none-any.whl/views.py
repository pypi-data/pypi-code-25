# -*- coding: utf-8 -*-
"""
    polls.views
    ~~~~~~~~~~~

    This module contains the views for the
    polls Plugin.

    :copyright: (c) 2018 by Михаил Лебедев.
    :license: BSD License, see LICENSE for more details.
"""
from flask import Blueprint, flash
from flask_babelplus import gettext as _

from flaskbb.utils.helpers import render_template
from flaskbb.plugins.models import PluginRegistry


polls_bp = Blueprint("polls_bp", __name__, template_folder="templates")


@polls_bp.route("/")
def index():
    plugin = PluginRegistry.query.filter_by(name="polls").first()
    if plugin and not plugin.is_installed:
        flash(_("Plugin is not installed."), "warning")

    return render_template("index.html", plugin=plugin)
