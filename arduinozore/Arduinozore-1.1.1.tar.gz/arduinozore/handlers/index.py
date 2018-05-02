"""Index page handler package."""

from arduinozore.handlers.baseHandler import BaseHandler
from arduinozore.models.device import Device


class IndexPageHandler(BaseHandler):
    """Index page handler."""

    def get(self):
        """Handle get request."""
        devices = Device.get_connected_devices()
        self.render('index.html', devices=devices)
