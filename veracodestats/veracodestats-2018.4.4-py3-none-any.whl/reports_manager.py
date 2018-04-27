import os
import xml.etree.cElementTree as cET
from veracodestats.api import VeracodeAPI, VeracodeAPIError


class ReportsManager:
    """A reports manager"""

    def __init__(self):
        self.api = VeracodeAPI()
        self.tag_template = "{{https://analysiscenter.veracode.com/schema/{0}/{1}list}}{1}"

    def download_reports(self, to_folder=None):
        if to_folder is None:
            return

        builds = []

        try:
            print("Downloading application list")
            apps = cET.fromstring(self.api.get_app_list()).findall(self.tag_template.format("2.0", "app"))

            for index, app in enumerate(apps):
                print("\rDownloading app build lists {}/{}".format(index + 1, len(apps)), end="")
                builds += cET.fromstring(self.api.get_build_list(app.attrib["app_id"]))\
                    .findall(self.tag_template.format("2.0", "build"))
                sandboxes = cET.fromstring(self.api.get_sandbox_list(app.attrib["app_id"]))\
                    .findall(self.tag_template.format("4.0", "sandbox"))
                for sandbox in sandboxes:
                    builds += cET.fromstring(self.api.get_build_list(app.attrib["app_id"], sandbox.attrib["sandbox_id"]))\
                        .findall(self.tag_template.format("2.0", "build"))
        except VeracodeAPIError as e:
            print("\r\nCould not download application list: {}".format(e))
            raise

        print("")

        for index, build in enumerate(builds):
            print("\rDownloading reports {}/{}".format(index + 1, len(builds)), end="")

            filename = build.attrib["build_id"] + ".xml"
            filepath = os.path.join(to_folder, filename)

            if not os.path.exists(filepath):
                try:
                    detailed_report_xml = self.api.get_detailed_report(build.attrib["build_id"])
                    with open(filepath, "wb") as f:
                        f.write(detailed_report_xml)
                except (VeracodeAPIError, IOError) as e:
                    print("\r\nFailed to save report for {}: {}".format(filename, e))
                    raise
