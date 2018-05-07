#!/usr/bin/env python3
"""
"""
import os
import sys
import argparse
import pprint
import hues
from .client import upload
from .builder import TarballBuilder


def build_argparse(environ=os.environ):
    parser = argparse.ArgumentParser(description="SpiroFS Deployment Client")
    parser.add_argument("project", help="Name of project to deploy to")
    parser.add_argument("deployment", help="Name of specific deployment inside of project to deploy to")
    parser.add_argument("--highstate", action="store_true", dest="highstate", default=True,
            help="Highstate after deployment (default)")
    parser.add_argument("--no-highstate", action="store_false", dest="highstate",
            help="Do not highstate")
    parser.add_argument("--artifact", action="append", metavar="PATH", default=(),
            help="Add the given file/directory into the bundle under _artifacts")
    parser.add_argument("--token", metavar="TOKEN", default=environ.get("SPIRO_TOKEN", "").strip(),
            help="Token to use to authenticate with the server")
    parser.add_argument("--server", metavar="URL", default=environ.get("SPIRO_URL", "https://salt:4510/").strip(),
            help="URL to POST to, defaults to https://salt:4510/")
    parser.add_argument("--insecure", action="store_false", dest="sslverify",
            help="Do not verify SSL certificates. EXTREMELY UNRECOMMENDED.")
    parser.add_argument("--ssl-cert", dest="sslverify", metavar="FILE",
            help="Key or CA to use for SSL key verification.")
    return parser


def _print_update(data):
    print("== {} ==".format(data['minion']))
    ret = data['result']['ret']
    if isinstance(ret, dict):
        states = sorted(ret.values(), key=lambda s: s.get('__run_num__'))
        for state in states:
            hs = hues.huestr(pprint.pformat(state))
            # FIXME: Only color if isatty
            if state['result']:
                print(hs.green.colorized)
            else:
                print(hs.red.colorized)
    elif isinstance(ret, list) and len(ret) == 1:
        hs = hues.huestr(ret[0])
        print(hs.red.colorized)
    else:
        pprint(ret)
    return data['result']['retcode']


EVENT_PRINTERS = {
    'highstate-update': _print_update,
}


def main(argv=sys.argv[1:]):
    args = build_argparse().parse_args(argv)
    print("Collecting files")
    with TarballBuilder() as builder:
        builder.add_gitcommit()
        if os.path.exists('_salt'):
            builder.add_saltdir('_salt')
        for a in args.artifact:
            builder.add_artifact(a, a)
    
    print("Uploading to server")
    rv = 0
    for event, data in upload(
        args.server,
        args.token,
        builder.buffer,
        args.project,
        args.deployment,
        highstate=args.highstate,
        sslverify=args.sslverify
    ):
        if event in EVENT_PRINTERS:
            rv = rv or EVENT_PRINTERS[event](data)
        elif 'msg' in data:
            print(data['msg'])
        else:
            print(event, pprint.pformat(data))

    return rv
