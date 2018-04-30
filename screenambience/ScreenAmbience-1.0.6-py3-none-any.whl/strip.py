from .message import set_zone_color

class LightStrip(object):
    """
    Contains information about the Lifx-Z Light Strip
    
    Attributes
        mac_address: the light strip's mac address
        zones: the number of zones that make up the strip

    """

    def __init__(self, mac, zones):
        self.mac_address = mac
        self.zones = zones

    def set_light_color(self, color, duration, zone_start, zone_end):
        set_zone_color(color, duration, self.mac_address, zone_start, zone_end)