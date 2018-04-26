def apps_scanned_by_year(apps):
    apps_scanned_by_year = {}

    for app in apps:
        for build in app.builds:
            build_year = build.published_date.year
            if build_year not in apps_scanned_by_year:
                apps_scanned_by_year[build_year] = {}
            if app.name not in apps_scanned_by_year[build_year]:
                apps_scanned_by_year[build_year][app.name] = 0
            apps_scanned_by_year[build_year][app.name] += 1

    return apps_scanned_by_year


def apps_compliant_by_year(apps):
    apps_compliant_by_year = {}

    for app in apps:
        last_year_with_a_pass = None
        for build in app.builds:
            build_year = build.published_date.year
            if build_year != last_year_with_a_pass and build.policy_rules_status == "Pass":
                last_year_with_a_pass = build_year
                if build_year not in apps_compliant_by_year:
                    apps_compliant_by_year[build_year] = []
                apps_compliant_by_year[build_year].append(app.id)

    return apps_compliant_by_year


def apps_scanned_by_year_by_policy(apps):
    apps_scanned_by_year_by_policy = {}

    for app in apps:
        builds_by_year = {}
        for build in app.builds:
            if build.published_date.year  not in builds_by_year:
                builds_by_year[build.published_date.year] = []
            builds_by_year[build.published_date.year].append(build)
        for year, builds in builds_by_year.items():
            if year not in apps_scanned_by_year_by_policy:
                apps_scanned_by_year_by_policy[year] = {}
            for build in builds:
                if build.policy_name not in apps_scanned_by_year_by_policy[year]:
                    apps_scanned_by_year_by_policy[year][build.policy_name] = []
                if app.name not in apps_scanned_by_year_by_policy[year][build.policy_name]:
                    apps_scanned_by_year_by_policy[year][build.policy_name].append(app.name)

    return apps_scanned_by_year_by_policy


def apps_scanned_by_year_by_month_by_scan_type(apps):
    apps_scanned_by_year_by_month_by_scan_type = {}

    for app in apps:
        for build in app.builds:
            build_year = build.published_date.year
            build_month = build.published_date.month
            if build_year not in apps_scanned_by_year_by_month_by_scan_type:
                apps_scanned_by_year_by_month_by_scan_type[build_year] = {}
            if build_month not in apps_scanned_by_year_by_month_by_scan_type[build_year]:
                apps_scanned_by_year_by_month_by_scan_type[build_year][build_month] = {}
            if app.name not in apps_scanned_by_year_by_month_by_scan_type[build_year][build_month]:
                apps_scanned_by_year_by_month_by_scan_type[build_year][build_month][app.name] = {"static": False, "dynamic": False}
            if not apps_scanned_by_year_by_month_by_scan_type[build_year][build_month][app.name][build.type]:
                apps_scanned_by_year_by_month_by_scan_type[build_year][build_month][app.name][build.type] = True

    return apps_scanned_by_year_by_month_by_scan_type
