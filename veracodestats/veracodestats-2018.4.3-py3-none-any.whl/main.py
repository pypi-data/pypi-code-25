import os
import calendar
import argparse
from veracodestats.data_manager import DataManager
from veracodestats.reports_manager import ReportsManager
from veracodestats import stats_manager


def run():
    parser = argparse.ArgumentParser(description="Generate interesting statistics for a Veracode account")
    parser.add_argument("report_folder", help="report save/load folder", type=str)
    parser.add_argument("-d", "--download",
                        help="download all reports, may take some time for large accounts",
                        action="store_true")
    args = parser.parse_args()

    try:
        if not os.path.exists(args.report_folder):
            os.makedirs(args.report_folder)
    except OSError:
        print("Could not create detailed report destination folder")
        return

    if args.download:
        ReportsManager().download_reports(to_folder=args.report_folder)

    data = DataManager()
    data.load_data(from_folder=args.report_folder)

    apps_scanned_by_year = stats_manager.apps_scanned_by_year(data.apps.values())
    apps_compliant_by_year = stats_manager.apps_compliant_by_year(data.apps.values())

    print("\r\nCompliance Rate By Year")
    print("-----------------------")
    print("{: <10}{: <10}{: <10}".format("Year", "%", "Compliant/Scanned"))
    for year, app_dict in sorted(apps_scanned_by_year.items()):
        compliant_apps_list = apps_compliant_by_year.get(year, [])
        print("{: <10}{: <10}{}/{}".format(year, round(100 * len(compliant_apps_list) / len(app_dict.items())),
                                           len(compliant_apps_list), len(app_dict.items())))

    apps_scanned_by_year_by_policy = stats_manager.apps_scanned_by_year_by_policy(data.apps.values())

    print("\r\nApps Scanned By Year By Policy")
    print("------------------------------")
    for year, policies in sorted(apps_scanned_by_year_by_policy.items()):
        print(year)
        print("{: <40}{: <10}".format("Policy", "Count"))
        for policy_name, app_list in sorted(policies.items(), key=lambda x: (-len(x[1]), x[0])):
            print("{: <40}{: <10}".format(policy_name, len(app_list)))
        print("")

    apps_scanned_by_year_by_month_by_scan_type = stats_manager.apps_scanned_by_year_by_month_by_scan_type(
        data.apps.values())

    print("\r\nApps Scanned By Year/Month By Scan Type")
    print("---------------------------------------")
    for year, months in sorted(apps_scanned_by_year_by_month_by_scan_type.items()):
        print(year)
        print("{: <10}{: <10}{: <10}".format("Month", "Static", "Dynamic"))
        for month, app_list in sorted(months.items()):
            static_count = sum(app["static"] for app in app_list.values())
            dynamic_count = sum(app["dynamic"] for app in app_list.values())
            print("{: <10}{: <10}{: <10}".format(calendar.month_abbr[month], static_count, dynamic_count))
        print("")


def start():
    try:
        run()
    except KeyboardInterrupt:
        print("\r\nExiting")


if __name__ == "__main__":
    start()
