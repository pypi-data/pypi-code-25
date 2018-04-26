"""Local settings."""

import os

SECRET_KEY = "secure!"
DEBUG = True

JIRA_URL = "https://jira.criteois.com/"
JIRA_USERNAME = os.environ.get("JIRA_USERNAME")
JIRA_PASSWORD = os.environ.get("JIRA_PASSWORD")

MLT_BOARDS = {
    "name": "Observability Interrupts",
    "description": """
# Observability Interrupts.

Documentation: https://confluence.criteois.com/pages/viewpage.action?pageId=323162482
Rotation: https://observability.crto.in/opsgenie/whoisoncall/SRE_Observability_interrupts
""",
    "link": "https://confluence.criteois.com/pages/viewpage.action?pageId=323162482",
    "filter": "project = OBS AND issuetype = Ticket AND Status != Closed",
    "scoring_strategy": "my_little_ticket.tickets.strategies.default",
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/django_cache",
    }
}

TICKETS_METRICS = True
