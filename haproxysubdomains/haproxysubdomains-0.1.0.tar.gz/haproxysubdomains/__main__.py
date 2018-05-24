import argparse

from pyhaproxy import config as c
from pyhaproxy.parse import Parser
from pyhaproxy.render import Render


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.set_defaults(command=None)

    cmd_subparsers = parser.add_subparsers()

    add_parser = cmd_subparsers.add_parser('add')
    add_parser.set_defaults(command='add')
    add_parser.add_argument('config_file')
    add_parser.add_argument('frontend')
    add_parser.add_argument('domain')
    add_parser.add_argument('subdomain')
    add_parser.add_argument('--host', default='127.0.0.1')
    add_parser.add_argument('port', type=int)

    del_parser = cmd_subparsers.add_parser('del')
    del_parser.set_defaults(command='del')
    del_parser.add_argument('config_file')
    del_parser.add_argument('frontend')
    del_parser.add_argument('subdomain')

    args = parser.parse_args()
    if not args.command:
        return

    config = Parser(args.config_file).build_configuration()
    if args.command == 'add':
        config = add(config, args.frontend, args.domain, args.subdomain, args.host, args.port)
    elif args.command == 'del':
        config = remove(config, args.frontend, args.subdomain)

    Render(config).dumps_to(args.config_file)


def add(config, frontend_name, domain, subdomain, host, port):
    frontend = config.frontend(frontend_name)
    if not frontend:
        raise ValueError('Could not locate')

    frontend.remove_acl(subdomain)
    frontend.add_acl(c.Acl(
        subdomain,
        'hdr(host) -i {sub}.{domain}'.format(sub=subdomain, domain=domain)))

    frontend.remove_usebackend(subdomain)
    frontend.add_usebackend(c.UseBackend(
        subdomain, 'if', subdomain))

    backend = config.backend(subdomain)
    if not backend:
        config.backends.append(c.Backend(
            subdomain,
            [c.Server(subdomain, host, port)]))
    else:
        backend.remove_server(subdomain)
        backend.add_server(c.Server(
            subdomain, host, port))

    return config


def remove(config, frontend_name, subdomain):
    frontend = config.frontend(frontend_name)
    if frontend:
        frontend.remove_acl(subdomain)
        frontend.remove_usebackend(subdomain)

    backend = config.backend(subdomain)
    if backend:
        config.backends.remove(backend)

    return config


if __name__ == '__main__':
    main()
