from .message import set_color

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

    def set_light_color(self, color, zone_start, zone_end):
        set_color(color, zone_start, zone_end, self.mac_address)