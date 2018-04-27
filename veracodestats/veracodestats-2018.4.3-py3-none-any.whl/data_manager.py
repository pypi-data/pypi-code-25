import os
import concurrent.futures
import xml.etree.cElementTree as cET
from veracodestats.model import App, Sandbox, Build


class DataManager:
    """A data manager"""

    def __init__(self):
        self.apps = {}

    @staticmethod
    def _read_report_file(report_filepath):
        with open(report_filepath, "r") as f:
            string = f.read()
            substrings = string.split("<severity level=\"5\"", maxsplit=1)
            if len(substrings) == 2:
                return substrings[0] + "</detailedreport>"

    def load_data(self, from_folder=None):
        report_filename_list = sorted(os.listdir(from_folder))
        report_filepath_list = [os.path.join(from_folder, report_filename) for report_filename in report_filename_list]

        unparsed_reports = []
        parsed_reports = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            count = 0
            for unparsed_report in executor.map(self._read_report_file, report_filepath_list):
                count += 1
                print("\rLoading report files: {}/{}".format(count, len(report_filepath_list)), end="")
                if unparsed_report is not None:
                    unparsed_reports.append(unparsed_report)
            print("")

        with concurrent.futures.ProcessPoolExecutor() as executor:
            count = 0
            for parsed_report in executor.map(cET.fromstring, unparsed_reports):
                count += 1
                print("\rParsing reports: {}/{}".format(count, len(unparsed_reports)), end="")
                if parsed_report.tag == "{https://www.veracode.com/schema/reports/export/1.0}detailedreport":
                    parsed_reports.append(parsed_report)
            print("")

        for index, report in enumerate(parsed_reports):
            print("\rProcessing reports {}/{}".format(index + 1, len(parsed_reports)), end="")

            app = self.apps.get(report.attrib["app_id"], App(report))
            build = Build(report)
            if build.sandbox_id:
                sandbox = app.sandboxes.get(build.sandbox_id, Sandbox(report))
                sandbox.builds.append(build)
                app.sandboxes[build.sandbox_id] = sandbox
            else:
                app.builds.append(build)
            self.apps[app.id] = app

        print("")
