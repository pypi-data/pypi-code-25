import os
import xml.etree.cElementTree as cET
import veracodestats.model as model


class DataManager:
    """A data manager"""

    def __init__(self):
        self.apps = {}

    @staticmethod
    def _read_report_file(report_filepath):
        with open(report_filepath, "r") as f:
            return f.read()

    def load_data(self, from_folder=None):
        report_filename_list = sorted(os.listdir(from_folder))
        report_filepath_list = [os.path.join(from_folder, report_filename) for report_filename in report_filename_list]
        report_filepath_count = len(report_filepath_list)

        for index, report_filepath in enumerate(report_filepath_list):
            print("\rProcessing reports {}/{}".format(index + 1, report_filepath_count), end="")

            unparsed_report = self._read_report_file(report_filepath)
            parsed_report = cET.fromstring(unparsed_report)

            if parsed_report.tag == "{https://www.veracode.com/schema/reports/export/1.0}detailedreport":
                app = self.apps.get(parsed_report.attrib["app_id"], model.App(parsed_report))
                build = model.Build(parsed_report)
                if build.sandbox_id:
                    sandbox = app.sandboxes.get(build.sandbox_id, model.Sandbox(parsed_report))
                    sandbox.builds.append(build)
                    app.sandboxes[build.sandbox_id] = sandbox
                else:
                    app.builds.append(build)
                self.apps[app.id] = app

        print("")
