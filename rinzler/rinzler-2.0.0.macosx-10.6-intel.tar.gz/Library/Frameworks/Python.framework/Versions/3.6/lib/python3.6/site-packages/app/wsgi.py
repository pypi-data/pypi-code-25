"""
WSGI config for ExemploAPI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

# API Root
# sys.path.insert(0, "/var/www/ExemploAPI/")

# Path da pasta site-packages/ que contém as dependências deste projeto(mod_wsgi only)
# sys.path.insert(1, "/var/www/ExemploAPI/lib/python3.5/site-packages/")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
