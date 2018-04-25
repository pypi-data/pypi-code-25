#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import clidye
import json
import os
import requests

import config as cfg

from flask import Flask, jsonify, request

# Our logger
logger = clidye.Clidye('trident-resin-proxy')

# And our flask app
app = Flask(__name__)

# Get environment variables
deviceUuid              = os.environ["RESIN_DEVICE_UUID"]
appId                   = os.environ["RESIN_APP_ID"]
supervisorToken         = os.environ["RESIN_SUPERVISOR_API_KEY"]
resinDataToken          = os.environ["RESIN_API_KEY"]
supervisorBaseUrl       = os.environ["RESIN_SUPERVISOR_ADDRESS"]

# Resin Data API Endpoints
resinDataBaseUrl_v1     = "https://api.resin.io/v1"
resinDataBaseUrl_v2     = "https://api.resin.io/v2"

# TODO: Put timeouts and exception checks on requests calls

# ---------------
# GET endpoints

# Ping
@app.route('/supervisor/ping', methods=['GET'])
def supervisor_ping():
    """Responds with a simple "OK", signaling that the supervisor is alive and well.
    """

    url = "{0}/ping?apikey={1}".format( supervisorBaseUrl, supervisorToken )
    header = { "Content-Type" : "application/json" }
    return requests.get( url, headers=header )

# Device State
@app.route('/supervisor/deviceState', methods=['GET'])
def supervisor_device_state():
    """Returns the current device state, as reported to the Resin API.
    """

    url = "{0}/v1/device?apikey={1}".format( supervisorBaseUrl, supervisorToken )
    header = { "Content-Type" : "application/json" }
    return requests.get( url, headers=header )

# App Info
@app.route('/supervisor/appInfo', methods=['GET'])
def supervisor_app_info():
    """Returns the current app ID, along with additional information such as commit, and environment variables.
    """

    url = "{0}/v1/apps/{1}?apikey={2}".format( supervisorBaseUrl, appId, supervisorToken )
    header = { "Content-Type" : "application/json" }
    return requests.get( url, headers=header )

# ---------------
# POST endpoints

# Check Update
@app.route('/supervisor/checkUpdate', methods=['POST'])
def supervisor_check_update():
    """Triggers an update check on the supervisor. Optionally, forces an update when updates are locked.
    """
    data = '{"force":true}'
    url = "{0}/v1/update?apikey={1}".format( supervisorBaseUrl, supervisorToken )
    header = { "Content-Type" : "application/json" }

    return requests.post( url, data, headers=header)

# Set Device to Commit
@app.route('/resin/setCommit', methods=['POST'])
def resin_set_commit():
    """Triggers an update check on the supervisor. Optionally, forces an update when updates are locked.
    """

    # Get the commit ID
    payload = request.get_json()
    commit = payload[ "commit" ]

    resinDataHeader = { "Authorization" : "Bearer {}".format( resinDataToken ) }

    # Fetch the build ID for this commit
    
    buildIdUrl = "{0}/build?$select=id,commit_hash&$filter=application%20eq%20{1}%20and%20commit_hash%20eq%20'{2}'".format( resinDataBaseUrl_v2, appId, commit )
    res = requests.get( buildIdUrl, headers=resinDataHeader )
    res.raise_for_status()
    ret_json = res.json()
    buildId = ret_json[ "d" ][ 0 ][ "id" ]

    # Fetch the device ID
    deviceIdUrl = "{0}/device?$select=id,uuid&$filter=uuid%20eq%20'{1}'".format( resinDataBaseUrl_v2, deviceUuid )
    res = requests.get( deviceIdUrl, headers=resinDataHeader )
    res.raise_for_status()
    ret_json = res.json()
    deviceId = ret_json[ "d" ][ 0 ][ "id" ]

    # Make request to resin to set commit
    header =  { "Authorization" : "Bearer {}".format( resinDataToken ) }
    deviceUrl = "{0}/device({1})".format( resinDataBaseUrl_v2, deviceId )
    payload = {'build': "{}".format(buildId) }
    res = requests.patch( deviceUrl, headers=header, data=payload )

    return res.content, res.status_code


def run():
    app.run(host=cfg.TRIDENT_RESIN_PROXY_HOST, port=cfg.TRIDENT_RESIN_PROXY_PORT)

if __name__ == "__main__":
    run()
