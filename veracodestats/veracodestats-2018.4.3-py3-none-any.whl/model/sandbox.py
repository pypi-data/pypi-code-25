class Sandbox:
    """A sandbox"""

    def __init__(self, detailed_report_xml):
        self.id = detailed_report_xml.attrib["sandbox_id"]
        self.app_id = detailed_report_xml.attrib["app_id"]
        self.name = detailed_report_xml.attrib["sandbox_name"]
        self.builds = []

    def __str__(self):
        return self.name
