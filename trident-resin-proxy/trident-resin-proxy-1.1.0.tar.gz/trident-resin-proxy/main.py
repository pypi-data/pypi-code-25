#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
import config as cfg
import clidye
import requests
from werkzeug.exceptions import BadRequest
from flask import Flask, jsonify, request

from _version import __version__

# Constants
RESIN_DATA_BASE_URL_V2  = "https://api.resin.io/v2"
REQUEST_TIMEOUT_SECS    = 3.0 

# Create logger instance
logger = clidye.Clidye('trident-resin-proxy')

# Create Flask App
app = Flask(__name__)

# Get environment variables
try:
    deviceUuid              = os.environ["RESIN_DEVICE_UUID"]
    appId                   = os.environ["RESIN_APP_ID"]
    supervisorToken         = os.environ["RESIN_SUPERVISOR_API_KEY"]
    resinDataToken          = os.environ["RESIN_API_KEY"]
    supervisorBaseUrl       = os.environ["RESIN_SUPERVISOR_ADDRESS"]
except Exception as err:
    logger.fatal( 'Could not find resin information in environment variables: {}'.format( err ) )
    sys.exit(1)

# ---------------
# GET endpoints

# Simple Availability Endpoint
@app.route('/version', methods=['GET'])
def version():
    """
    Responds with a 200 response. Useful for checking for availability.

    Returns:
        tuple(content,status_code):
            On Success: ({"version":<semver>}, 200)
            On Error:   ({}, 500)
    """
    try:
        logger.info( "GET: {0} FROM: {1}".format( request.url, request.remote_addr ) )

        resp = { "version" : __version__ }
        logger.info( "SUCCESS" )
        return json.dumps( resp ), requests.codes.ok
    except Exception as err:
        logger.error( "ERROR: {}".format( err ) )
        return "{}", requests.codes.internal_server_error

# Image Version
@app.route('/imageVersion', methods=['GET'])
def imageVersion():
    """
    Responds with the semantic version of the resin image.

    Returns:
        tuple(content,status_code):
            On Success: ({"version":<semver>}, 200)
            On Error:   ({}, 500)
    """
    try:
        logger.info( "GET: {0} FROM: {1}".format( request.url, request.remote_addr ) )

        resp = { "version" : os.environ["OROV_RESIN_IMAGE_SEMVER"] }
        logger.info( "SUCCESS" )
        return json.dumps( resp ), requests.codes.ok
    except Exception as err:
        logger.error( "ERROR: {}".format( err ) )
        return "{}", requests.codes.internal_server_error

# Ping
@app.route('/supervisor/ping', methods=['GET'])
def supervisor_ping():
    """
    Responds with a simple "OK", signaling that the supervisor is alive and well.

    Returns:
        tuple(content,status_code):
            On Success: ("", 200)
            On Timeout: ("", 408)
            On Error:   ("", upstream_status_code)
    """
    try:
        logger.info( "GET: {0} FROM: {1}".format( request.url, request.remote_addr ) )
        url     = "{0}/ping?apikey={1}".format( supervisorBaseUrl, supervisorToken )
        res     = requests.get( url, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()

        logger.info( "SUCCESS" )
        return "", requests.codes.ok
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "", e.response.status_code

# Device State
@app.route('/supervisor/deviceState', methods=['GET'])
def supervisor_device_state():
    """
    Gets the current device state, as reported to the Resin API.
    
    Returns:
        JSON String:
            On Success: (json_data, 200)
            On Timeout: ({}, 408)
            On Error:   ({}, upstream_status_code)

    Contents include (example):
    {
        "status": "Idle", 
        "os_variant": "prod", 
        "download_progress": null, 
        "update_failed": false, 
        "api_port": 48484, 
        "ip_address": "192.168.1.220", 
        "supervisor_version": "6.6.0", 
        "os_version": "Resin OS 2.9.7+rev1",
        "update_pending": false, 
        "update_downloaded": false, 
        "commit": "0b167ef90f6b00a56ac58b8fe6842b7b179599b9"
    }
    """

    try:
        logger.info( "GET: {0} FROM: {1}".format( request.url, request.remote_addr ) )
        url = "{0}/v1/device?apikey={1}".format( supervisorBaseUrl, supervisorToken )
        res     = requests.get( url, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()

        logger.info( "SUCCESS" )
        return json.dumps( res.json() ), requests.codes.ok
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code

# App Info
@app.route('/supervisor/appInfo', methods=['GET'])
def supervisor_app_info():
    """
    Gets the current app ID, along with additional information such as commit, and environment variables.  

    Returns:
        JSON String:
            On Success: (json_data, 200)
            On Timeout: ({}, 408)
            On Error:   ({}, upstream_status_code)

    Contents include:
    {
        "containerId": <docker container ID>,
        "imageId": "registry2.resin.io/v2/<docker image ID>", 
        "appId": <app ID>, 
        "env": 
        { 
            <all environment variables present in the device container> 
        }
    }
    """

    try:
        logger.info( "GET: {0} FROM: {1}".format( request.url, request.remote_addr ) )
        url = "{0}/v1/apps/{1}?apikey={2}".format( supervisorBaseUrl, appId, supervisorToken )
        res     = requests.get( url, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()

        logger.info( "SUCCESS" )
        return json.dumps( res.json() ), requests.codes.ok
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code

# ---------------
# POST endpoints

# Check Update
@app.route('/supervisor/checkUpdate', methods=['POST'])
def supervisor_check_update():
    """
    Triggers an update check on the supervisor. Optionally, forces an update when updates are locked.
    Returns:
        JSON String:
            On Success: ({}, 200)
            On Timeout: ({}, 408)
            On Error:   ({}, upstream_status_code)
    """

    try:
        logger.info( "POST: {0} FROM: {1}".format( request.url, request.remote_addr ) )
        url = "{0}/v1/update?apikey={1}".format( supervisorBaseUrl, supervisorToken )
        header = { "Content-Type" : "application/json" }
        res     = requests.post( url, headers=header, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()

        logger.info( "SUCCESS" )
        return "{}", requests.codes.ok
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code

# Reboot
@app.route('/supervisor/reboot', methods=['POST'])
def supervisor_reboot():
    """
    Triggers a reboot of the container.
    Returns:
        JSON String:
            On Success: ({}, 200)
            On Timeout: ({}, 408)
            On Error:   ({}, upstream_status_code)
    """

    try:
        logger.info( "POST: {0} FROM: {1}".format( request.url, request.remote_addr ) )
        url = "{0}/v1/reboot?apikey={1}".format( supervisorBaseUrl, supervisorToken )
        header = { "Content-Type" : "application/json" }
        res     = requests.post( url, headers=header, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()

        logger.info( "SUCCESS" )
        return "{}", requests.codes.ok
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code


# Set Device to Commit
@app.route('/resin/setCommit', methods=['POST'])
def resin_set_commit():
    """
    Communicates with the remote resin service and sets the vehicle's release to the specified commit.

    JSON String:
            On Success:         ({}, 200)
            On Timeout:         ({}, 408)
            On Invalid Payload: ({}, 400)
            On Upstream Error:  ({}, upstream_error)
            On Generic Error:   ({}, 500)
    """

    logger.info( "POST: {0} FROM: {1}".format( request.url, request.remote_addr ) )

    # Get the commit ID
    try:
        payload = request.get_json(force=True)
        commit = payload[ "commit" ]
        payload
        logger.info( commit )
    except Exception as err:
        logger.error( "Invalid request: {}".format( err ) )
        return "{}", requests.codes.bad_request

    resinDataHeader = { "Authorization" : "Bearer {}".format( resinDataToken ) }

    # Fetch the build ID for the specified commit
    try:
        logger.info( "Fetching build ID..." )
        buildIdUrl = "{0}/build?$select=id,commit_hash&$filter=application%20eq%20{1}%20and%20commit_hash%20eq%20'{2}'".format( RESIN_DATA_BASE_URL_V2, appId, commit )
        res = requests.get( buildIdUrl, headers=resinDataHeader, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()
        ret_json = res.json()
        buildId = ret_json[ "d" ][ 0 ][ "id" ]
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code
    except Exception as err:
        logger.error( "ERROR: {}".format( err ) )
        return "{}", requests.codes.internal_server_error

    # Fetch the device ID
    try:
        logger.info( "Fetching device ID..." )
        deviceIdUrl = "{0}/device?$select=id,uuid&$filter=uuid%20eq%20'{1}'".format( RESIN_DATA_BASE_URL_V2, deviceUuid )
        res = requests.get( deviceIdUrl, headers=resinDataHeader, timeout=REQUEST_TIMEOUT_SECS )
        res.raise_for_status()
        ret_json = res.json()
        deviceId = ret_json[ "d" ][ 0 ][ "id" ]
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code
    except Exception as err:
        logger.error( "ERROR: {}".format( err ) )
        return "{}", requests.codes.internal_server_error

    # Make request to resin to set commit
    try:
        logger.info( "Sending commit request..." )
        header =  { "Authorization" : "Bearer {}".format( resinDataToken ) }
        deviceUrl = "{0}/device({1})".format( RESIN_DATA_BASE_URL_V2, deviceId )
        payload = {'build': "{}".format(buildId) }
        res = requests.patch( deviceUrl, headers=header, data=payload )

        logger.info( "SUCCESS" )
        return "{}", requests.codes.ok
    except requests.exceptions.Timeout:
        logger.error( "TIMEOUT" )
        return "{}", requests.codes.timeout
    except requests.exceptions.RequestException as e:
        logger.error( "ERROR: {}".format( e ) )
        return "{}", e.response.status_code

def run():
    try:
        app.run(host=cfg.TRIDENT_RESIN_PROXY_HOST, port=cfg.TRIDENT_RESIN_PROXY_PORT)
    except Exception as err:
        logger.fatal( "Service failure: {}".format( err ) )

if __name__ == "__main__":
    run()
