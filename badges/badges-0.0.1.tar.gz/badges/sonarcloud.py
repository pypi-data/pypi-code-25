#!/usr/bin/env python
from badges.badge import Badge

# https://sonarcloud.io/api/project_badges/measure?project=name&metric=key
# metric=bugs                   bugs
# metric=code_smells            code_smells
# metric=sqale_rating           maintainability     (dublicated with codeclimate badge)
# metric=alert_status           Quality Gate        (passed. no need)
# metric=reliability_rating     reliability
# metric=security_rating        security_rating
# metric=sqale_index            Tech debt           (time. no need)
# metric=vulnerabilities        vulnerabilities


class Sonarcloud(Badge):
    title = "Sonarcloud"
    image = "https://sonarcloud.io/api/project_badges/measure?project={project}&metric={metric}"
    link = "https://sonarcloud.io/dashboard?id={project}"

    def __init__(self, project, metric):
        self.project = project
        self.metric = metric
        # todo: validate metric
