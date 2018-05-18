"""mp-starter bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as StarterBaseController.

from mp_starter.cli.controllers.base import StarterBaseController


def load(app):
    app.handler.register(StarterBaseController)
