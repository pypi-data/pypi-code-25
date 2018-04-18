import json
from . import base_dashboard,api
from . import models
def create_dashboard(title_dashboard,panels,object_project_id):
    dashboard = base_dashboard.get_dashboard()
    dashboard['title'] = title_dashboard
    dashboard['panels'] = panels
    #base['panels'] = panels
    # for panel in panels:
    #     dashboard['panels'].append(panel)
    print("DASHBOARD COMPLETO:   ",dashboard)
    api.create_dashboard(object_project_id,dashboard)
    #return base

def update_dashboard(panels,object_project_id):
    dashboard = models.DashboardGrafana.objects.get(object_project=object_project_id)
    json_dashboard = dashboard.dashboard_content
    for panel in panels:
        json_dashboard['panels'].append(panel)
    api.update_dashboard(dashboard.uid,json_dashboard)