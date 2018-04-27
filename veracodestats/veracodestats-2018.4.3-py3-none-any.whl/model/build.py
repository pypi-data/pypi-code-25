import pytz
from datetime import datetime


class Build:
    """A build"""

    def __init__(self, detailed_report_xml):
        analysis_element = detailed_report_xml.find("{https://www.veracode.com/schema/reports/export/1.0}static-analysis")
        self.type = "static"
        if analysis_element is None:
            analysis_element = detailed_report_xml.find("{https://www.veracode.com/schema/reports/export/1.0}dynamic-analysis")
            self.type = "dynamic"

        self.id = detailed_report_xml.attrib["build_id"]
        self.app_id = detailed_report_xml.attrib["app_id"]
        self.sandbox_id = detailed_report_xml.attrib.get("sandbox_id")
        self.version = detailed_report_xml.attrib["version"]
        self.published_date = datetime.strptime(analysis_element.attrib["published_date"],
                                                "%Y-%m-%d %H:%M:%S %Z").astimezone(pytz.utc)
        self.first_build_submitted_date = datetime.strptime(detailed_report_xml.attrib["first_build_submitted_date"],
                                                            "%Y-%m-%d %H:%M:%S %Z").astimezone(pytz.utc)
        self.is_latest_build = detailed_report_xml.attrib["is_latest_build"]
        self.policy_name = detailed_report_xml.attrib["policy_name"]
        self.policy_version = detailed_report_xml.attrib["policy_version"]
        self.policy_rules_status = detailed_report_xml.attrib["policy_rules_status"]
        self.score = analysis_element.attrib["score"]
        # The following three attributes are only relevant for builds where is_latest_build == "true"
        self.policy_compliance_status = detailed_report_xml.attrib["policy_compliance_status"]
        self.grace_period_expired = detailed_report_xml.attrib["grace_period_expired"]
        self.scan_overdue = detailed_report_xml.attrib["scan_overdue"]

    def __str__(self):
        return self.version
