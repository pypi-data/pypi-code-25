# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PyScadaReportConfig(AppConfig):
    name = 'pyscada.report'
    verbose_name = _("PyScada Report Daemon")
