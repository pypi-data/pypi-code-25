#!/usr/bin/env python3


### bimeta client ###

import json
import argparse
from termcolor import colored
from datetime import datetime
import sys
import re
import csv
import hmac
import hashlib
import requests
import yaml
import os


# Hacked up derivative of argparse.Action used to make argparse provide correct help on things like ./bimeta get user --help 
class customHelp(argparse.Action):
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        self.helpStr = kwargs['help']
        kwargs['nargs'] = 0
        super(customHelp, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(self.helpStr)
        setattr(namespace, self.dest, values)
        sys.exit(0)


class bimeta:
    def __init__(self, sslVerify=True):
        self.sslVerify = sslVerify
        self.completedPage = 0
        self.completedIndex = 0
        self.vv = False
        # TODO
        self.clientVersion = '1.3'
        self.clientVersion = '1.2'
        self.defaultAffiliation = 'all'
        pageSize = 100

        self.fields = dict()
        self.fields['pageSize'] = pageSize
        self.fields['affiliation'] = ['affiliation', 'type', 'comment']
        self.fields['user'] = ['name', 'title', 'affiliation', 'email', 'clearance', 'comm', 'tech', 'exe']
        self.fields['authcred'] = ['email']
        self.fields['authorization'] = ['email', 'action', 'verb', 'constraintName', 'constraintValue']
        self.fields['credsource'] = ['name', 'date', 'meta']
        self.fields['cred'] = ['username', 'credential', 'affiliation', 'source']
        self.fields['ip'] = ['ip', 'affiliation', 'type']
        self.fields['keyword'] = ['keyword', 'affiliation', 'type']
        self.fields['domain'] = ['domain', 'affiliation', 'type']
        self.fields['role'] = ['name', 'description', 'type']
        self.fields['userrole'] = ['email', 'rolename']
        self.fields['roleperm'] = ['role', 'action', 'verb', 'constraintName', 'constraintValue']
        self.fields['tag'] = ['type', 'target', 'name', 'value']

    def main(self, arguments=sys.argv):
        self.args = arguments

        parser = argparse.ArgumentParser(description='bimeta client',
                                         usage='''bimeta <command> [<args>]
    Commands: get|put|set|delete|check|configure''',
                                         epilog=colored('blueintel', 'blue', 'on_white') + colored(' -tr', 'cyan'))
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(self.args[1:2])
        # if user is trying to run configure - allow them to do that
        if args.command == 'configure':
            self.configure()
            sys.exit(0)

        # all other functionality requires a configuration file:
        ret = self.getConfig()
        self.apiKey = ret['apiKey']
        self.apiUrl = ret['apiUrl']
        self.awsApiKey = ret['awsApiKey']
        self.apiSecret = ret['apiSecret']
        self.defaultAffiliation = ret['defaultAffiliation']

        if not hasattr(self, args.command):
            raise ValueError('Unrecognized command. Try --help')
        getattr(self, args.command)()

    def __findConfigFile(self):
        # if BIMETA_CFG is set - use that
        try:
            return os.environ['BIMETA_CFG']
        except:
            pass
        path = os.path.expanduser("~/.bimeta/bimeta.config")
        if os.path.isfile(path):
            return path
        path = "{}/bimeta.config".format(os.path.dirname(os.path.realpath(__file__)))
        if os.path.isfile(path):
            return path
        path = "{}/bimeta.config".format(os.getcwd())
        if os.path.isfile(path):
            return path
        raise ValueError("Unable to locate bimeta configuration file. Please run bimeta configure.")

    def getConfig(self):
        ''' Loads the bimeta.config configuration file, validates key fields, returns a dictionary. File is located as follows:
            1. Check ~/.bimeta/bimeta.config
            2. Check location of the bimeta.py script
            3. Check CWD
            First found file will be used.
         '''
        configFile = self.__findConfigFile()
        try:
            cfg = yaml.load(open(configFile))
        except Exception as e:
            raise ValueError("Could not load bimeta.config: {}".format(str(e)))

        #
        # Verify that all required fields are defined:
        try:
            cfg['defaultAffiliation']
            cfg['apiKey']
            cfg['apiSecret']
            cfg['awsApiKey']
            cfg['apiUrl']
        except Exception as e:
            raise ValueError("ERR: Invalid configuration file: {}. Error: {}".format(configFile, str(e)))

        return cfg

    def postRequest(self, data, headers, apiUrl, awsApiKey, bpApiKey, bpApiSecret):
        ''' Sends bimeta api request with provided data and headers to apiUrl using awsApiKey.  Signs requests per bimeta spec using bpApiKey
            and bpApiSecret.  Current time on the machine must be accurate.  Time skews exceeding 30 seconds result in failed signatures. '''
        self.awsApiKey = awsApiKey
        self.apiKey = bpApiKey
        self.apiSecret = bpApiSecret
        self.apiUrl = apiUrl
        return self.__postRequest(data, headers)

    def __postRequest(self, data, headers=dict()):
        jsonData = json.dumps(data)
        sigHeaders = self.__genSignatureHeaders(jsonData)
        allHeaders = sigHeaders.copy()
        allHeaders.update(headers)
        allHeaders['content-type'] = 'application/json'
        allHeaders['user-agent'] = 'bimeta'
        allHeaders['version'] = self.clientVersion
        allHeaders['x-api-key'] = self.awsApiKey
        if self.vv:
            print(colored('HEADERS', 'white'))
            print(json.dumps(allHeaders))
            print(colored('DATA', 'white'))
            print(json.dumps(data))
        req = requests.post(self.apiUrl, data=json.dumps(data), headers=allHeaders, verify=self.sslVerify)
        if self.vv:
            print(colored('RESPONSE STATUS CODE', 'white'))
            print(req.status_code)
            print(colored('RESPONSE', 'white'))
            print(req.text)
        if req.status_code == 400:
            tmp = json.loads(req.text)
            raise ValueError('Request failed: ' + tmp['data'])
        elif req.status_code != 200:
            raise ValueError('Request failed: ' + req.text)

        return req.text

    def __genSignatureHeaders(self, data):
        ''' HMAC signs the message using the apiKey and apiSecret from bimeta.config. Returns a dict of headers including an HMAC signature
            Any change to data will invalidate the signature.  Headers may be appended to prior to sending. '''
        headers = dict()
        headers['bp-key'] = self.apiKey
        headers['bp-time'] = datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S')
        toSign = headers['bp-time'] + headers['bp-key'] + data
        hmacSignature = hmac.new(bytes(self.apiSecret.encode()), toSign.encode(), hashlib.sha512).hexdigest().lower()
            
        headers['bp-auth'] = hmacSignature
        return headers

    def check(self):
        parser = argparse.ArgumentParser(description='Check data', prog='bimeta check')
        parser.add_argument('-vv', help=argparse.SUPPRESS, action='store_true')
        parser.add_argument('--noverify', help='Accept unverifiable certificates', action='store_true')
        subparsers = parser.add_subparsers(help='VERB - type of data to check')

        # cred
        helpStr = colored('Check creds', 'white') + ' Format: username,credential,affiliation'
        subparser = subparsers.add_parser('cred', help=helpStr, add_help=False)
        subparser.add_argument('-h', '--help', help=helpStr, action=customHelp)
        subparser.set_defaults(checkVerb='cred')

        parser.add_argument('-f', '--file', help='Read input from file (instead of STDIN)', type=argparse.FileType('r'))
        args = parser.parse_args(self.args[2:])
        if args.vv: self.vv = True
        if args.noverify:
            self.sslVerify = False
            requests.packages.urllib3.disable_warnings()

        if args.file:
            dataSrc = args.file
        else:
            dataSrc = sys.stdin

        more = True
        while more:
            ret = self.__readBatch(dataSrc, self.fields['pageSize'], args.checkVerb)
            batchStartLine = (self.completedPage - 1) * self.fields['pageSize'] + 1
            batchEndLine = (self.completedIndex)
            more = ret['more']
            # Execute the request.  Lines being submitted in this batch are:
            # From (inclusive): (self.completedPage-1)*self.fields['pageSize']+1)
            # To (inclusive): (self.completedIndex)
            if len(ret['data']) == 0: continue
            req = dict()
            req['data'] = ret['data']
            req['action'] = 'put'
            req['verb'] = args.getVerb
            ret = self.__postRequest(req)
            ret = json.loads(ret)
            if ret['status'] == 'success':
                print(colored('rows (' + str(batchStartLine) + '-' + str(batchEndLine) + ') completed.', 'white'))
            else:
                # print colored('Failed ', 'red')+colored(' submiting rows '+str(batchStartLine)+'-'+str(batchEndLine), 'white')
                raise ValueError(colored('Failed ', 'red') + colored(
                    ' submiting rows ' + str(batchStartLine) + '-' + str(batchEndLine), 'white'))

    def delete(self):
        parser = argparse.ArgumentParser(description='Delete data', prog='bimeta del')
        parser.add_argument('-vv', help=argparse.SUPPRESS, action='store_true')
        parser.add_argument('--noverify', help='Accept unverifiable certificates', action='store_true')
        subparsers = parser.add_subparsers(help='VERB - type of data to delete')

        # user
        subparser = subparsers.add_parser('user', help='Delete user')
        subparser.set_defaults(delVerb='user')
        subparser.add_argument('email', help='user email')

        subparser = subparsers.add_parser('org', help='Delete org')
        subparser.set_defaults(delVerb='affiliation')
        subparser.add_argument('affiliation', help='org name')

        subparser = subparsers.add_parser('keyword', help='Delete keyword')
        subparser.set_defaults(delVerb='keyword')
        subparser.add_argument('keyword', help='keyword')
        subparser.add_argument('affiliation', help='affiliation name')

        subparser = subparsers.add_parser('domain', help='Delete domain')
        subparser.set_defaults(delVerb='domain')
        subparser.add_argument('domain', help='domain name')
        subparser.add_argument('affiliation', help='affiliation')

        subparser = subparsers.add_parser('role', help='Delete role')
        subparser.set_defaults(delVerb='role')
        subparser.add_argument('role', help='role name')

        subparser = subparsers.add_parser('config', help='Delete configuration file')
        subparser.set_defaults(delVerb='config')
        subparser.add_argument('affiliation', help='affiliation')
        subparser.add_argument('name', help='config name')

        subparser = subparsers.add_parser('tag', help='Delete a tag')
        subparser.set_defaults(delVerb='tag')
        subparser.add_argument('type', help='Type of tag to delete', choices=['user', 'affiliation'])
        subparser.add_argument('target', help='Target object whose tag we are deleting (e.g. orgname or email)')
        subparser.add_argument('tag', help='Tag name')

        args = parser.parse_args(self.args[2:])
        if args.vv:
            self.vv = True
        if args.noverify:
            self.sslVerify = False
            requests.packages.urllib3.disable_warnings()

        req = dict()
        req['action'] = 'delete'
        req['verb'] = args.delVerb
        req['data'] = list()
        ignore = ['vv', 'noverify', 'delVerb']
        tmp = dict()
        for key, value in vars(args).items():
            if key in ignore: continue
            tmp[key] = value
        req['data'].append(tmp)

        ret = self.__postRequest(req)
        parsedRet = json.loads(ret)
        if isinstance(parsedRet['data'], list) and len(parsedRet['data']) != 0:
            print(json.dumps(parsedRet['data'], indent=4))

    def get(self):
        parser = argparse.ArgumentParser(description='Retrieve data', prog='bimeta get')
        parser.add_argument('-vv', help=argparse.SUPPRESS, action='store_true')
        parser.add_argument('--noverify', help='Accept unverifiable certificates', action='store_true')
        subparsers = parser.add_subparsers(help='VERB - type of data to retrieve.')

        # user
        userParser = subparsers.add_parser('user', help='Retrieve user data')
        userParser.set_defaults(getVerb='user')
        userParser.add_argument('--affiliation', help='...for specified org')
        userParser.add_argument('--email', help='...matching specified email')
        userParser.add_argument('--clearance', help='...matching specified clearance')
        userParser.add_argument('--type', help='...from orgs of specified type')
        userParser.add_argument('--comm', choices=['true', 'false'], help='...with comm flag set as specified')
        userParser.add_argument('--tech', choices=['true', 'false'], help='...with tech flag set as specified')
        userParser.add_argument('--exe', choices=['true', 'false'], help='...with exe flag set as specified')
        userParser.add_argument('--tag', help='...with the specified name=value tag')

        # ip
        ipParser = subparsers.add_parser('ip', help='Retrieve IP data')
        ipParser.set_defaults(getVerb='ip')
        ipParser.add_argument('--ip', help='...matching specified IP')
        ipParser.add_argument('--affiliation', help='...matching specified org')
        ipParser.add_argument('--type', help='...matching specified type')
        ipParser.add_argument('--before', help='...added before specified date')
        ipParser.add_argument('--after', help='...added after specified date')

        # tags
        tagsParser = subparsers.add_parser('tag', help='Retrieve tags')
        tagsParser.set_defaults(getVerb='tag')
        tagsParser.add_argument('type', help='Type of object to inspect', choices=['user', 'affiliation'])
        tagsParser.add_argument('target', help='Target to inspect (e.g. org name or email address)')

        # config files
        configParser = subparsers.add_parser('config', help='Retrieve configuration files')
        configParser.set_defaults(getVerb='config')
        configParser.add_argument('--affiliation', help='...matching specified org', required=True)
        configParser.add_argument('--name', help='...matching specified name', required=True)

        # affiliation
        affilParser = subparsers.add_parser('org', help='Retrieve orgs')
        affilParser.set_defaults(getVerb='affiliation')
        affilParser.add_argument('--affiliation', help='Retrieve a specified org entry')
        affilParser.add_argument('--type', help='...of specified type')
        affilParser.add_argument('--before', help='...registered before provided date')
        affilParser.add_argument('--after', help='...registered after provided date')
        affilParser.add_argument('--tag', help='...with the specified name=value tag')

        # cred
        credParser = subparsers.add_parser('cred', help='Retrieve tracked compromised credentials')
        credParser.set_defaults(getVerb='cred')
        credParser.add_argument('--source', help='...from the provided source')
        credParser.add_argument('--affiliation', help='...for the provided org')
        credParser.add_argument('--username', help='...matching the provided username')
        credParser.add_argument('--before', help='...added before provided date')
        credParser.add_argument('--after', help='...added after provided date')
        credParser.add_argument('--uniq', action='store_true',
                                help='...only show unique matches (combine with --source)')

        # credSource
        credSourceParser = subparsers.add_parser('credsource',
                                                 help='Retrieve tracked sources of compromised credentials')
        credSourceParser.set_defaults(getVerb='credsource')
        credSourceParser.add_argument('--before', help='...collected before the specified date')
        credSourceParser.add_argument('--after', help='...collected after the specified date')
        credSourceParser.add_argument('--name', help='...with the specified source name')
        credSourceParser.add_argument('--affiliation', help='...with matches for provided org')

        # keyword
        keywordParser = subparsers.add_parser('keyword', help='Retrieve keywords')
        keywordParser.set_defaults(getVerb='keyword')
        keywordParser.add_argument('--affiliation', help='..for specified org')
        keywordParser.add_argument('--keyword', help='...matching specified keyword')
        keywordParser.add_argument('--type', help='...matching specified keyword type')

        # authorizations
        authParser = subparsers.add_parser('authorization', help='Retrieve authorization data')
        authParser.set_defaults(getVerb='authorization')
        authParser.add_argument('--affiliation', help='...for specified org')
        authParser.add_argument('--email', help='...for specified user email')

        # authcred
        authCredParser = subparsers.add_parser('authcred', help='Retrieve authentication credentials')
        authCredParser.set_defaults(getVerb='authcred')
        authCredParser.add_argument('--email', help='...for specified user')
        authCredParser.add_argument('--affiliation', help='...for specified org')

        # role
        roleParser = subparsers.add_parser('role', help='Retrieve roles')
        roleParser.set_defaults(getVerb='role')
        roleParser.add_argument('--role', help='...for specified role name')
        roleParser.add_argument('--type', help='...for specified type')

        # roleperm
        rolePermParser = subparsers.add_parser('roleperm', help='Retrieve role permissions')
        rolePermParser.set_defaults(getVerb='roleperm')
        rolePermParser.add_argument('--role', help='...for specified role name')

        # userrole
        userRoleParser = subparsers.add_parser('userrole', help='Retrieve user to role mappings')
        userRoleParser.set_defaults(getVerb='userrole')
        userRoleParser.add_argument('--role', help='...for specified role name')
        userRoleParser.add_argument('--email', help='...for specified user')
        userRoleParser.add_argument('--type', help='...for roles of specified type')
        userRoleParser.add_argument('--affiliation', help='...for users from specified org')

        parser.add_argument('--json', action='store_true', help='Return results as json')
        args = parser.parse_args(self.args[2:])
        if args.vv:
            self.vv = True
        if args.noverify:
            self.sslVerify = False
            requests.packages.urllib3.disable_warnings()

        # behold this hax and despair
        ignoreItems = ['json', 'getVerb', 'vv', 'noverify']
        req = dict()
        req['action'] = 'get'
        req['verb'] = args.getVerb
        req['filter'] = list()
        hasAffiliation = False
        argVars = vars(args)
        for key in argVars:
            if argVars[key] == None or key in ignoreItems: continue
            if key == 'affiliation': hasAffiliation = True
            req['filter'].append({'name': key, 'value': argVars[key]})
        if not hasAffiliation:
            req['filter'].append({'name': 'affiliation', 'value': self.defaultAffiliation})

        more = True
        # keeps track of which page we're requesting for multipage requests
        reqPage = 0
        fullDataAllPages = list()
        while more:
            req['startPage'] = reqPage
            try:
                ret = self.__postRequest(req)
            except Exception as e:
                raise
            parsedRet = json.loads(ret)
            if isinstance(parsedRet['data'], list):
                fullDataAllPages.extend(parsedRet['data'])
            else:
                print(ret)

            if not parsedRet['more']: break
            reqPage += 1

        if len(fullDataAllPages) > 0:
            print(json.dumps(fullDataAllPages, indent=4))

    def set(self):
        parser = argparse.ArgumentParser(description='Set properties', prog='bimeta set')
        parser.add_argument('-vv', help=argparse.SUPPRESS, action='store_true')
        parser.add_argument('--noverify', help='Accept unverifiable certificates', action='store_true')
        subparser = parser.add_subparsers(help='VERB - type of record to modify properties for')

        # user
        userParser = subparser.add_parser('user', help='Set user properties')
        userParser.set_defaults(setVerb='user')
        userParser.add_argument('email', help='Target user')
        userParser.add_argument('--clearance', choices=['white', 'green', 'amber', 'red'], help='set clerance')
        userParser.add_argument('--comm', choices=['true', 'false'], help='set comm flag')
        userParser.add_argument('--tech', choices=['true', 'false'], help='set tech flag')
        userParser.add_argument('--exe', choices=['true', 'false'], help='set exe flag')
        userParser.add_argument('--title', help='set title')

        # org
        orgParser = subparser.add_parser('org', help='Set org properties')
        orgParser.set_defaults(setVerb='org')
        orgParser.add_argument('org', help='Target org')
        orgParser.add_argument('--type', choices=['badpanda', 'salamander', 'toad', 'newt'], help='set org type')
        orgParser.add_argument('--comment', help='set org comment')

        args = parser.parse_args(self.args[2:])
        if args.vv: self.vv = True
        if args.noverify:
            self.sslVerify = False
            requests.packages.urllib3.disable_warnings()

        if args.setVerb == 'user':
            # behold this hax and despair
            ignoreItems = ['json', 'setVerb', 'vv', 'noverify']
            req = dict()
            req['action'] = 'get'
            req['verb'] = 'user'
            req['filter'] = list()
            req['filter'].append({'name': 'affiliation', 'value': self.defaultAffiliation})
            req['filter'].append({'name': 'email', 'value': args.email})

            retJson = self.__postRequest(req)
            ret = json.loads(retJson)
            if ret['status'] != 'success':
                print(colored('Failed ', 'red') + 'locating user.')
                return
            req = dict()
            req['action'] = 'put'
            req['verb'] = 'user'
            req['data'] = list()
            userrow = ret['data'][0]
            userrow.pop('userkey', None)
            userrow.pop('type', None)
            argVars = vars(args)
            for key in argVars:
                if argVars[key] == None or key in ignoreItems: continue
                userrow[key] = argVars[key]
            req['data'].append(userrow)
            retJson = self.__postRequest(req)
            ret = json.loads(retJson)
            if ret['status'] == 'success':
                print(colored('Success', 'white'))
            else:
                print(colored('Failed ', 'red'))
            return

    def put(self):
        parser = argparse.ArgumentParser(description='Put data', prog='bimeta put')
        parser.add_argument('-vv', help=argparse.SUPPRESS, action='store_true')
        parser.add_argument('--noverify', help='Accept unverifiable certificates', action='store_true')
        subparsers = parser.add_subparsers(help='VERB - type of data to submit')

        # user
        userHelpStr = colored('Submit users.', 'green') + '  Format: ' + ','.join(self.fields['user'])
        userParser = subparsers.add_parser('user', help=userHelpStr, add_help=False)
        userParser.add_argument('-h', '--help', help=userHelpStr, action=customHelp)
        userParser.set_defaults(getVerb='user')

        # ip
        ipHelpStr = colored('Submit IPs.', 'green') + ' Format: ' + ','.join(self.fields['ip'])
        ipParser = subparsers.add_parser('ip', help=ipHelpStr, add_help=False)
        ipParser.add_argument('-h', '--help', help=ipHelpStr, action=customHelp)
        ipParser.set_defaults(getVerb='ip')

        # tag
        tagHelpStr = colored('Submit tags.', 'green') + ' Format: ' + ','.join(self.fields['tag'])
        tagParser = subparsers.add_parser('tag', help=tagHelpStr, add_help=False)
        tagParser.add_argument('-h', '--help', help=tagHelpStr, action=customHelp)
        tagParser.set_defaults(getVerb='tag')

        # affiliation
        affilHelpStr = colored('Submit orgs.', 'green') + ' Format: ' + ','.join(self.fields['affiliation'])
        affilParser = subparsers.add_parser('org', help=affilHelpStr, add_help=False)
        affilParser.add_argument('-h', '--help', help=affilHelpStr, action=customHelp)
        affilParser.set_defaults(getVerb='affiliation')

        # cred
        credHelpStr = colored('Submit creds.', 'green') + ' Format: ' + ','.join(self.fields['cred'])
        credParser = subparsers.add_parser('cred', help=credHelpStr, add_help=False)
        credParser.add_argument('--affiliation', help='...org to which credentials belong', required=True)
        credParser.add_argument('-h', '--help', help=credHelpStr, action=customHelp)
        credParser.set_defaults(getVerb='cred')

        # credSource
        credSourceHelpStr = colored('Submit cred sources.', 'green') + ' Format: ' + ','.join(self.fields['credsource'])
        credSourceParser = subparsers.add_parser('credsource', help=credSourceHelpStr, add_help=False)
        credSourceParser.add_argument('-h', '--help', help=credSourceHelpStr, action=customHelp)
        credSourceParser.set_defaults(getVerb='credsource')

        # keyword

        keywordHelpStr = colored('Submit keywords.', 'green') + ' Format: ' + ','.join(self.fields['keyword'])
        keywordParser = subparsers.add_parser('keyword', help=keywordHelpStr, add_help=False)
        keywordParser.add_argument('-h', '--help', help=keywordHelpStr, action=customHelp)
        keywordParser.set_defaults(getVerb='keyword')

        # authorizations

        authHelpStr = colored('Submit authorizations.', 'green') + ' (use "all" to grant all) Format: ' + ','.join(
            self.fields['authorization'])
        authParser = subparsers.add_parser('authorization', help=authHelpStr, add_help=False)
        authParser.add_argument('-h', '--help', help=authHelpStr, action=customHelp)
        authParser.set_defaults(getVerb='authorization')

        # authcred
        authCredHelpStr = colored('Submit auth credentials.', 'green') + ' Format: ' + ','.join(self.fields['authcred'])
        authCredParser = subparsers.add_parser('authcred', help=authCredHelpStr, add_help=False)
        authCredParser.add_argument('-h', '--help', help=authCredHelpStr, action=customHelp)
        authCredParser.set_defaults(getVerb='authcred')

        # role
        roleHelpStr = colored('Submit a role.', 'green') + ' Format: ' + ','.join(self.fields['role'])
        authCredParser = subparsers.add_parser('role', help=roleHelpStr, add_help=False)
        authCredParser.add_argument('-h', '--help', help=roleHelpStr, action=customHelp)
        authCredParser.set_defaults(getVerb='role')

        # role permission
        rolePermHelpStr = colored('Submit a role permission.', 'green') + ' Format: ' + ','.join(
            self.fields['roleperm'])
        authCredParser = subparsers.add_parser('roleperm', help=rolePermHelpStr, add_help=False)
        authCredParser.add_argument('-h', '--help', help=rolePermHelpStr, action=customHelp)
        authCredParser.set_defaults(getVerb='roleperm')

        # userrrole
        roleHelpStr = colored('Assign a user to a role.', 'green') + ' Format: ' + ','.join(self.fields['userrole'])
        authCredParser = subparsers.add_parser('userrole', help=roleHelpStr, add_help=False)
        authCredParser.add_argument('-h', '--help', help=roleHelpStr, action=customHelp)
        authCredParser.set_defaults(getVerb='userrole')

        # configFile
        configHelpStr = colored('Submit a configuration file.', 'green')
        configParser = subparsers.add_parser('config', help=configHelpStr, add_help=True)
        configParser.add_argument('--affiliation', help='...for provided affiliation', required=False)
        configParser.add_argument('--name', help='...save as provided name', required=True)
        configParser.set_defaults(getVerb='config')

        parser.add_argument('--test', help='Parse input and print results only.', action='store_true')
        parser.add_argument('--json', help='Treat input as json', action='store_true')
        parser.add_argument('-f', '--file', help='Read input from file (instead of STDIN)', type=argparse.FileType('r'))
        args = parser.parse_args(self.args[2:])
        if args.vv: self.vv = True
        if args.noverify:
            self.sslVerify = False
            requests.packages.urllib3.disable_warnings()

        if args.file:
            dataSrc = args.file
        else:
            dataSrc = sys.stdin

        # config verb is different than others so we handle it here:
        if args.getVerb == 'config':
            req = dict()
            req['action'] = 'put'
            req['verb'] = 'config'
            req['data'] = list()
            fileRecord = dict()
            fileRecord['name'] = args.name
            if args.affiliation:
                fileRecord['affiliation'] = args.affiliation
            elif self.defaultAffiliation.lower() == "all":
                raise ValueError(
                    "Your default affiliation is ALL. You must specify the affiliation to upload a config file")
            else:
                fileRecord['affiliation'] = self.defaultAffiliation

            fileRecord['content'] = dataSrc.read()
            req['data'].append(fileRecord)
            ret = self.__postRequest(req)
            ret = json.loads(ret)
            if ret['status'] == 'success':
                print(colored('success', 'white'))
            else:
                print(colored('Failed', 'red'))
            return

        # all other verbs are handled here as generics:
        more = True
        while more:
            ret = self.__readBatch(dataSrc, self.fields['pageSize'], args.getVerb)
            batchStartLine = (self.completedPage - 1) * self.fields['pageSize'] + 1
            batchEndLine = (self.completedIndex)
            more = ret['more']
            # Execute the request.  Lines being submitted in this batch are:
            # From (inclusive): (self.completedPage-1)*self.config.pageSize+1)
            # To (inclusive): (self.completedIndex)
            if len(ret['data']) == 0: continue
            req = dict()
            req['data'] = ret['data']
            req['action'] = 'put'
            req['verb'] = args.getVerb
            ret = self.__postRequest(req)
            ret = json.loads(ret)
            if ret['status'] == 'success':
                print(colored('rows (' + str(batchStartLine) + '-' + str(batchEndLine) + ') completed.', 'white'))
            else:
                print(colored('Failed ', 'red') + colored(
                    ' submiting rows ' + str(batchStartLine) + '-' + str(batchEndLine), 'white'))

    def __readBatch(self, dataSrc, pageSize, verb):
        '''
        Reads pageSize entries from provided dataSrc, validates entries based on provided verb 
        Can call multiple times with same dataSrc to batch more.  Maintains state between multiple calls.
        You can NOT call this with more than one dataSrc throughout the lifetime of the program.
        Returns a dict: 
            ret['data'] holds an array of dicts representing pageSize or less rows
            ret['more'] holds a boolean specifying is more calls to __readBatch are needed to process the whole file
         
        '''

        retVal = dict()
        retVal['data'] = list()
        retVal['more'] = True
        try:
            self.fields[verb]
        except Exception as e:
            raise ValueError('Missing fields definition for verb: ' + verb + ' in appconfig.  Correct and rerun')

        # bit of a mess but it works could be improved by associating filedescriptor with a set of completedIndex and completedPage variables
        # Fine for now.
        lineIndex = 0
        csvReader = csv.reader(dataSrc, delimiter=',', quotechar='"')
        for lineIndex, line in enumerate(csvReader):
            retRow = dict()
            if len(line) != len(self.fields[verb]):
                raise ValueError(
                    'Format error in input on line ' + str(self.completedIndex + lineIndex + 1) + ' (expected: ' + str(
                        len(self.fields[verb])) + ' found: ' + str(len(line)) + ')')
            for index, field in enumerate(self.fields[verb]):
                retRow[field] = line[index]
            retVal['data'].append(retRow)
            if (lineIndex + 1) % pageSize == 0:
                self.completedPage += 1
                self.completedIndex = self.completedIndex + lineIndex + 1
                return retVal

        retVal['more'] = False
        self.completedPage += 1
        self.completedIndex = self.completedIndex + lineIndex + 1
        return retVal

    def configure(self):
        if os.name == 'nt':
            print("Save configuration as bimeta.config and place it in the same folder as bimeta.py")
            sys.exit(0)

        print("Paste your configuration file (end with ctrl+d)")
        cnfLines = []
        for line in sys.stdin:
            cnfLines.append(line)

        # Set the umask to user only for files about to be created
        os.umask(0o77)
        bimetaConfigPath = os.path.expanduser("~/.bimeta")
        try:
            os.makedirs(bimetaConfigPath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise ValueError("Unable to create folder: {}".format(bimetaConfigPath))
        try:
            conf = open('{}/bimeta.config'.format(bimetaConfigPath), 'w')
        except:
            raise ValueError("Unable to write to configuration file: {}/bimeta.config".format(bimetaConfigPath))

        conf.writelines(cnfLines)
        conf.close()
        print("Configuration complete.")


def bimetamain():
    try:
        myMain = bimeta()
        myMain.main(sys.argv)
    except Exception as e:
        if os.environ.get('BIMETA_DEBUG'):
            raise
        sys.stderr.write(colored('ERROR: ', 'red') + colored(str(e), 'white') + '\n')
        sys.exit(-1)
if __name__ == '__main__':
    bimetamain()
