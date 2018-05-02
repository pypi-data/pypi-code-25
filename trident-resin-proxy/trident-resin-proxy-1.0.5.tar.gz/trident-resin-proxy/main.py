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

# Image Version
@app.route('/imageVersion', methods=['GET'])
def supervisor_ping():
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
    Gets the current app ID, along with additional information such as commit, and environment variables.    Returns:
        JSON String:
            On Success: (json_data, 200)
            On Timeout: ({}, 408)
            On Error:   ({}, upstream_status_code)
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

# Set Device to Commit
@app.route('/resin/setCommit', methods=['POST'])
def resin_set_commit():
    """Triggers an update check on the supervisor. Optionally, forces an update when updates are locked.
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
