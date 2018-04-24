import argparse


def main():
    desc = 'Shakespeare is a auth system which uses Nginx X-Accel'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--host', action='store',
                        default='127.0.0.1',
                        help='Server interface')
    parser.add_argument('--port', action='store',
                        default=8099,
                        help='Server port')
    args = parser.parse_args()
    from .server import run_server
    run_server(args.host, args.port)
