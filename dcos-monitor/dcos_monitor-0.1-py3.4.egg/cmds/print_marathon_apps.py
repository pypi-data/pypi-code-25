import click
import copy
import json
import requests
import socket
import time
from dcos_monitor.cli import get_json, login, pass_context
from dcos_monitor.util import dget, lpad, print_separator

# Hack to get working in proxy environment (basically ignores proxy)
session = requests.Session()
session.trust_env = False

@click.command('print_full_status', short_help='Print out a full status report of the cluster')
@pass_context
def cli(ctx, wait):
    """print out a full status report on the cluster
    """
    print("Marathon Apps")
    print_separator()
    print("")
    GET_MARATHON = True
    SHOW_INACTIVE = False
    token = login(ctx.master, ctx.marathon_user, ctx.marathon_password)
    apps, json_string = get_marathon_apps(ctx.master, token)
    print_marathon_apps(apps, GET_MARATHON, SHOW_INACTIVE)

def get_marathon_apps(hostname, token):
    if hostname is None:
        hostname = socket.gethostname()
    headers = {'authorization': "token={token}".format(token=token)}
    response = session.get("http://{hostname}/marathon/v2/apps".format(hostname=hostname),
                 headers=headers)
    not_json = response.json()
    return not_json['apps'], response.text

def print_marathon_apps(apps, level, show_inactive):
    app_dict = {app['id']:app for app in apps}
    for app_id in sorted(app_dict.keys()): # Need to implement sorting
        app = app_dict[app_id]
        if app['instances'] > 0 or show_inactive == True:
            # print(app_id)
            print_app(app, level)
            # print(app_dict[app_id])
            # print(json.dumps(app_dict[app_id]))
            print("")

def print_app(app, level):
    resource_string="    {resource:<8}: {amount:<6} {unit:<6} "
    
    print_separator(80, '-')

    # print(json.dumps(app))
    # print_separator(40, '-')

    if app['instances'] == 0:
        print("{app:<40} ** INACTIVE **".format(app=app['id']))
    else:
        print("{app:<40} ** ACTIVE [{running} Tasks Running] **".format(app=app['id'], running=app['tasksRunning']))
    print_separator(80, '-')
    # print("{id}".format(id=app['id']))
    lpad("Roles:           {}".format('*' if 'acceptedResourceRoles' not in app or app['acceptedResourceRoles'] == None else 
                                       app['acceptedResourceRoles'] if len(app['acceptedResourceRoles']) == 1 else 
                                       ','.join(app['acceptedResourceRoles'])))
    print("")    
    lpad("Docker Image:    {}".format(dget(app,['container','docker','image'],'N/A')))
    print("")
    lpad("Command:")
    lpad("{}".format(app['cmd']),8)
    print("")
    # print("Resources:")
    lpad("{} Instance(s), each with:".format(app['instances']))
    if app['cpus'] > 0:
        lpad(resource_string.format(amount=app['cpus'], unit='Cores', resource='CPU'))
    if app['gpus'] > 0:        
        lpad(resource_string.format(amount=app['gpus'], unit='Cores', resource='GPU'))
    if app['mem'] > 0:        
        lpad(resource_string.format(amount=app['mem'], unit='MB', resource='Memory'))
    if app['disk'] > 0:        
        lpad(resource_string.format(amount=app['disk'], unit='MB', resource='Disk'))
    # print("    {cpus:<4} Cores".format(cpus=app['cpus']))
    # print("    {} GPU Core".format(gpus=app['gpus']))
    # print("    {} MB Memory".format(mem=app['mem']))
    # print("    {} MB Disk".format(disk=app['disk']))
    # print("          {} Cores\n, {} GPUs\n, {} MB Memory\n, {} MB Disk\n".format(app['cpus'], app['gpus'], app['mem'], app['disk']))
    print("")
    if len(app['ports']) > 0 and len(app['ports']) < 10:
        lpad("Ports:")
        for port in app['ports']:
            lpad(" - {}".format(port))
        print("")
    elif len(app['ports']) >= 10:
        lpad("Ports: " + ','.join(str(x) for x in app['ports']))
        print("")

    if len(app['uris']) > 0:
        lpad("URIs:")
        for uri in app['uris']:
            lpad(" - {}".format(uri),4)
    if level > 1:
        if len(app['env']) > 0:
            print("")
            lpad("Environment Variables:")
            for v in sorted(app['env']):
                lpad("\"{}\" : \"{}\"".format(v, app['env'][v]), 8)
        if len(app['labels']) > 0:
            print("")
            lpad("Labels:")
            for v in sorted(app['labels']):
                lpad("\"{}\" : \"{}\"".format(v, app['labels'][v]), 8)

