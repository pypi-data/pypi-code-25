# -*- coding: utf-8 -*-

### imports ###################################################################
import calendar
import datetime
import os
import threading
import time
import yaml

### imports from ##############################################################
# from flask import redirect
from flask import render_template
from flask import request
from flask import send_file

### relaitve imports from #####################################################
from . import app

### global variables ##########################################################
cal_dict = dict((value, key) for key, value in enumerate(calendar.month_abbr))

fullfile = os.path.join('config', 'vertex_70_mock.cfg')

with open(fullfile) as f:
    parameterDict = yaml.load(f)
    
filenames = parameterDict['filenames']

global_dict = {
        'filename': 'hello.0',
        'filenames': filenames,
        'in_use_since': 'Mon, 12 Jan 2018 15:13:08',
        'rest_scans': 0,
        'rest_time': 0,
        'scans': 0,
        'SNR': 0,
        'spectrum_counter': 0,
        'status': 'IDL',
        'start_scan': False,
        }

### helper functions ##########################################################
def get_date():
    dateStr = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
    return dateStr

def get_template(page_name):
    dateStr = get_date()

    return render_template(
            page_name,
            dateStr=dateStr,
            host=request.host,
            global_dict=global_dict)

### views #####################################################################
@app.route("/")
def index():
    return get_template('index.htm')


@app.route('/brow_cmd.htm')
@app.route('/menubasic.htm')
def brow_cmd():
    dateStr = get_date()
    
    html_dict = {
            'Acquisition': 'brow_cmd_Acquisition.htm',
            'Basic': 'brow_cmd.htm',
            'Advanced': 'brow_cmd_Advanced.htm',
            'Optic': 'brow_cmd_Optic.htm',
            'FT': 'brow_cmd_FT.htm'
    }

    Ume = request.args.get('Ume', default='Basic')

    if Ume in html_dict.keys():
        html = html_dict[Ume]
    else:
        return 'not implemented yet'
        
    return render_template(html, dateStr=dateStr, host=request.host, Ume=Ume)


@app.route('/diag.htm')
def diagnostics():
    return get_template('brow_diag.htm')


@app.route('/cmd.htm')
def cmd():
    if 'UNI' in request.args.keys():
        for key, cmd in request.args.items():
            if key == 'UNI':
                param, value = cmd.split('=')
                global_dict[param] = value
                
                '''
                if param == 'SNR':
                    global_dict['filename'] = value + '_pos.0'
                '''
    else:
        for param, value in request.args.items():
            global_dict[param] = value
            
            if param == 'NSS':
                global_dict['rest_scans'] = 10
                global_dict['rest_time'] = 20.0
            elif param == 'WRK':
                if value == '3':
                    str_counter = str(global_dict['spectrum_counter'])
                    filename = 'a' + str_counter.zfill(4) + '.0'

                    global_dict['filename'] = filename
                    global_dict[filename] = int(global_dict['SNR'])
                    global_dict['spectrum_counter'] += 1
                    global_dict['start_scan'] = True
                    
                    print(global_dict)

    if global_dict['start_scan']:
        global_dict['start_scan'] = False
        t = threading.Thread(target=scan, args=(global_dict,))
        t.start()
                
    return render_template('cmd.htm', global_dict=global_dict)


def scan(parameters):
    parameters['status'] = 'SCN'
    
    elapsed_time = 0.
    duration = parameters['rest_time']
    N = parameters['rest_scans']
    start_time = time.time()

    dNdt = N / duration

    while elapsed_time < duration:
        i = round(dNdt * elapsed_time)
        parameters['rest_scans'] = N - i
        parameters['rest_time'] = round(duration - elapsed_time)
        elapsed_time = time.time() - start_time

    parameters['rest_scans'] = 0
    parameters['rest_time'] = 0
    parameters['status'] = 'IDL'


@app.route('/directcmd.htm')
def directcmd():
    for key, cmd in request.args.items():
        if key == 'UNI':
            param, value = cmd.split('=')
            global_dict[param] = value
            
            if param == 'LSR' and value == '0':
                global_dict['status'] = 'ERR'
                
            if param == 'LSR' and value == '1':
                global_dict['status'] = 'IDL'
    
    return get_template('directcmd.htm')


@app.route('/config/')
def config():
    return get_template('config.htm')


@app.route('/config/cmdlist.htm')
def cmdlist():
    return render_template('cmdlist.htm', global_dict=global_dict)

    
@app.route('/config/hardware/')
def hardware():
    return render_template('hardware.htm', host=request.host)


@app.route('/config/<string:page_name>')
def config_page(page_name):
    return get_template(page_name)


@app.route('/stat.htm')
def status():
    return render_template('/stat.htm', global_dict=global_dict)


@app.route('/favicon.ico')
def favicon():
    return send_file('static/' + 'favicon.ico')

@app.route('/<string:filename>.0')
def download_scan(filename):
    filename = filename + '.0'
    sample_position = global_dict[filename]
    filename = global_dict['filenames'][sample_position]
    return send_file('downloads/' + filename)

 
@app.route('/<string:page_name>')
def static_page(page_name):
    return get_template(page_name)


    

