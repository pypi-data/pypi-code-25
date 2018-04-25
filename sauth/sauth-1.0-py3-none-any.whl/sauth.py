"""
Sauth:
A simple authenticated web server handler
license="GNU General Public License v3"
"""

__version__ = 1.0
__prog__ = 'sauth'

from http.server import SimpleHTTPRequestHandler
import os
import sys
import base64
import ssl
import socketserver
import click


CERT_FILE = os.path.expanduser("~/.ssh/cert.pem")
KEY_FILE = os.path.expanduser("~/.ssh/key.pem")
SSL_CMD = "openssl req -newkey rsa:2048 -new -nodes -x509 " \
          "-days 3650 -keyout {0} -out {1}".format(KEY_FILE, CERT_FILE)


class SimpleHTTPAuthHandler(SimpleHTTPRequestHandler):
    """Main class to present webpages and authentication."""
    username = ''
    password = ''

    def __init__(self, request, client_address, server):
        key = '{}:{}'.format(self.username, self.password).encode('ascii')
        self.key = base64.b64encode(key)
        self.valid_header = b'Basic ' + self.key
        super().__init__(request, client_address, server)

    def do_HEAD(self):
        """head method"""
        print("send header")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_authhead(self):
        """do authentication"""
        print("send header")
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"Test\"")
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """Present frontpage with user authentication."""
        auth_header = self.headers.get('Authorization', '').encode('ascii')
        if auth_header is None:
            self.do_authhead()
            self.wfile.write(b"no auth header received")
        elif auth_header == self.valid_header:
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.do_authhead()
            self.wfile.write(auth_header)
            self.wfile.write(b"not authenticated")


def serve_http(ip="", port=80, https=True, start_dir=None, handler_class=SimpleHTTPAuthHandler):
    """setting up server"""
    httpd = socketserver.TCPServer((ip, port), handler_class)

    if https:
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=KEY_FILE,
                                       certfile=CERT_FILE, server_side=True)

    if start_dir:
        print("Changing dir to {cd}".format(cd=start_dir))
        os.chdir(start_dir)

    socket_addr = httpd.socket.getsockname()
    print('Serving "{}" directory on {}://{}:{}'.format(
        os.getcwd(), 'https' if https else 'http', socket_addr[0], socket_addr[1])
    )
    httpd.serve_forever()


@click.command()
@click.argument('username')
@click.argument('password')
@click.argument('ip', default='0.0.0.0')
@click.argument('port', default=8333)
@click.option('--https', help='use https', is_flag=True)
@click.option('--dir', help='use different directory')
def main(dir, ip, port, username, password, https):
    """
    Start http server with basic authentication current directory.
    """
    if https and not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
        print(file=sys.stderr)
        print("Missing {} or {}".format(CERT_FILE, KEY_FILE), file=sys.stderr)
        print("Run `{}`".format(SSL_CMD), file=sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)

    SimpleHTTPAuthHandler.username = username
    SimpleHTTPAuthHandler.password = password
    serve_http(ip=ip, port=port, https=https,
               start_dir=dir, handler_class=SimpleHTTPAuthHandler)


if __name__ == "__main__":
    main()
