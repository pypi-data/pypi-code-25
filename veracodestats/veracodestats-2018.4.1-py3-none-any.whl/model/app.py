class App:
    """An app"""

    def __init__(self, detailed_report_xml):
        self.id = detailed_report_xml.attrib["app_id"]
        self.name = detailed_report_xml.attrib["app_name"]
        self.business_owner = detailed_report_xml.attrib["business_owner"]
        self.business_unit = detailed_report_xml.attrib["business_unit"]
        self.tags = detailed_report_xml.attrib["tags"]
        self.sandboxes = {}
        self.builds = []

    def __str__(self):
        return self.name
