import os
import sys
import json
import datetime
import socket
import yaml
from flask import Flask, abort, Response, make_response, request


def print_request_line(status_code):
    """
    Print requests to stdout.
    :param status_code: HTTP status code.
    :return: None
    """
    print('{remote_addr} - - [{date}] "{method} {path} {version}" {status}'
          .format(remote_addr=request.remote_addr,
                  date=datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S'),
                  method=request.method,
                  path=request.url,
                  version=request.environ.get('SERVER_PROTOCOL'),
                  status=status_code))


class Index(object):
    """Response object for all paths other than credentials."""
    def __init__(self, config):
        self.config = config
        self._script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        with open("{0}/proxy.yaml".format(self.config['config_dir'])) as filehandler:
            self.data = yaml.load(filehandler.read())

    def __call__(self, *args, **kwargs):
        sys.stdout.flush()
        status_code = 200
        mime_type = 'text/plain'
        if kwargs:
            version = kwargs['branch'].split('/')[0]

            if version == 'latest':
                version = self.data['latest']

            branch = '/' + '/'.join(kwargs['branch'].split('/')[1:])

            try:
                data = self.data['paths'][version][branch]
            except KeyError:
                status_code = 404
                resp = Proxy.file_not_found_404()
            else:
                resp = list()
                if isinstance(data, list):
                    for i in data:
                        tmp_branch = branch
                        if tmp_branch != '/':
                            tmp_branch = tmp_branch + '/' + i

                        if not isinstance(self.data['paths'][version][tmp_branch], str):
                            resp.append(i + '/')
                        else:
                            resp.append(i)
                elif isinstance(data, dict):
                    resp = json.dumps(data)
                elif isinstance(data, str):
                    resp = data
        else:
            resp = list()
            data = self.data['paths']['/']
            for i in data:
                resp.append(i)

        if isinstance(resp, list):
            resp = '\n'.join(resp)

        print_request_line(status_code)
        return Response(response=resp, status=status_code, headers={}, mimetype=mime_type)


class Credentials(object):
    """Credentials response object."""
    def __init__(self, config):
        self.config = config
        self.token_filename = "{0}/tokens.json".format(self.config['config_dir'])
        self.credentials = self.get_tokens()
        self._script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    def __call__(self, *args, **kwargs):
        status_code = 200
        mime_type = 'text/plain'
        credentials = self.get_tokens()
        if 'role' in kwargs:
            # This ensures we only respond for the Role we obtained credentials for, otherwise return 404.
            if kwargs['role'] == credentials['LastRole'].split('/').pop():
                resp = json.dumps({
                    'Expiration': credentials['Expiration'],
                    'Token': credentials['Token'],
                    'SecretAccessKey': credentials['SecretAccessKey'],
                    'AccessKeyId': credentials['AccessKeyId'],
                    'Type': credentials['Type'],
                    'LastUpdated': credentials['LastUpdated'],
                    'Code': credentials['Code'],
                })
            else:
                resp = Proxy.file_not_found_404()
                status_code = 404
        else:
            resp = credentials['LastRole'].split('/').pop()

        print_request_line(status_code)
        return Response(response=resp, status=status_code, headers={}, mimetype=mime_type)

    def get_tokens(self):
        """
        Read tokens from tokens.json file.
        :return: None
        """
        try:
            with open(self.token_filename) as filehandler:
                self.credentials = json.loads(filehandler.read())
        except IOError:
            abort(make_response("Cannot open token file for reading.", 404))

        return self.credentials


class Proxy(object):
    app = None

    def __init__(self, config, args):
        self.config = config
        self.app = Flask(__name__)
        self.app.url_map.strict_slashes = False  # Match urls regardless of trailing slash

        self.app.debug = args.debug

        self.token_filename = "{0}/tokens.json".format(self.config['config_dir'])

        index = Index(self.config)
        self.app.add_url_rule('/', 'index', index)
        self.app.add_url_rule('/<path:branch>/', 'index_path', index)

        self.credentials = Credentials(self.config)
        self.app.add_url_rule('/<path:version>/meta-data/iam/security-credentials/', 'credentials', self.credentials)
        self.app.add_url_rule('/<path:version>/meta-data/iam/security-credentials/<path:role>/', 'credentials_role',
                              self.credentials)

    def run(self):
        try:
            self.app.run(host='169.254.169.254', port=80, use_reloader=False)
        except socket.error as e:
            if e.strerror == 'Permission denied' and e.errno == 13:
                print("Unable to bind to port 80. Please run as root.")
            exit(1)

    @staticmethod
    def file_not_found_404():
        return """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <title>404 - Not Found</title>
</head>
<body>
  <h1>404 - Not Found</h1>
</body>
</html>"""


if __name__ == '__main__':
    print("proxy.py is supposed to be included as a module, not run by itself. Exiting.")
    exit(1)
