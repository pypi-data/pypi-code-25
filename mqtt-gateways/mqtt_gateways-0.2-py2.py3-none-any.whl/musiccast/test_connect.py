'''
Created on 28 Apr 2017

@author: PierPaolo
'''

import httplib
import time

import json

devices = {
     'RXA550': ['192.168.1.42']
    ,'CDNT670D': ['192.168.1.44']
    }

dev_RXA550 = "192.168.1.42"
dev_CDNT670D = "192.168.1.44"

def request(connection, qualifier, command, arguments = None, method = 'GET', version = 'v1'):
    # format for arguments is /command?arg1=value1&arg2=value2&arg3=value3
    if arguments is not None:
        comtext = ''.join((command,'?','&'.join(['='.join(arg) for arg in arguments])))
    else: comtext = command
    reqtext = '/'.join(('/YamahaExtendedControl',version,qualifier,comtext))
    print reqtext
    connection.request(method,reqtext)
    response = connection.getresponse()
    print response.status, response.reason
    return response.read()

def main():
    t = time.time()
    connCD = httplib.HTTPConnection(dev_CDNT670D, timeout=1)
    connAV = httplib.HTTPConnection(dev_RXA550, timeout=0.1)
    conn = connAV
    dt = (time.time() - t) * 1000.0; t = time.time(); print 'instantiation ', dt, 'ms'

# YamahaExtendedControl/v1/main/setPower?power=on

    command = 'getFeatures' # 'setPower?power=on'
    qualifier = 'system'
    arguments = None # [['num', '29'], ['text', 'BBCLondon']]# [['band','dab']]
    data = request(conn,command=command,qualifier=qualifier, arguments=arguments)
    print data
    #dicto = json.loads(data)
    #print dicto['power']
    dt = (time.time() - t) * 1000.0; t = time.time(); print 'read ', dt, ' ms'
    
    return
    
    resp = request(connCD,command='setPlayback?playback=play',qualifier='cd')
    print resp
    
    
    connCD.close()
    connAV.close()
    return

    conn.request("GET","/YamahaExtendedControl/v1/main/setInput?input=cd")
    dt = time.time() - t; t = time.time(); print 'request 2', dt
    r = conn.getresponse()
    dt = time.time() - t; t = time.time(); print 'getresponse ', dt
    print r.status, r.reason
    print r.read()
    dt = time.time() - t; t = time.time(); print 'read ', dt
    
    conn.request("GET", "/YamahaExtendedControl/v1/cd/setPlayback?playback=stop")
    dt = time.time() - t; t = time.time(); print 'request 3', dt
    r = conn.getresponse()
    dt = time.time() - t; t = time.time(); print 'getresponse ', dt
    print r.status, r.reason
    print r.read()
    dt = time.time() - t; t = time.time(); print 'read ', dt
    
    conn.close()
    dt = time.time() - t; t = time.time(); print 'close ', dt

if __name__ == '__main__':
    main()