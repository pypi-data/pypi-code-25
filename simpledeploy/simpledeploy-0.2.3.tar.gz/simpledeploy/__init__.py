import argparse
import simpledeploy.build
import simpledeploy.deploy
import simpledeploy.destroy
import simpledeploy.modify

def main():
    helpStrings = {
        'name': 'The name of the deployment',
        'replicas': 'The number of replicas for the deployment',
        'review': 'Enable the deployment in review mode',
        'from': 'What Docker image this build should build from'
    }

    # The main argument parser for the application.
    mainParser = argparse.ArgumentParser(description='Deployment bridge between Gitlab and Kubernetes')
    subParsers = mainParser.add_subparsers(title='commands', dest='command')

    # The deployment parser command line interface.
    deployParser = subParsers.add_parser('deploy', help='Deploy the current project to Kubernetes')
    deployParser.add_argument('name', help=helpStrings['name'])
    deployParser.add_argument('--review', help=helpStrings['review'], action='store_true')
    deployParser.add_argument('--replicas', help=helpStrings['replicas'], action='store', default='1')

    # The build parser command line interface.
    buildParser = subParsers.add_parser('build', help='Build the existing artifacts into a Docker image')
    buildParser.add_argument('name', help=helpStrings['name'])
    buildParser.add_argument('--from', help=helpStrings['from'], action='store', required=True)

    # The destruction parser command line interface.
    destroyParser = subParsers.add_parser('destroy', help='Destroy the deployment in Kubernetes')
    destroyParser.add_argument('name', help=helpStrings['name'])
    destroyParser.add_argument('--review', help=helpStrings['review'], action='store_true')

    # The modification parser command line interface.
    modifyParser = subParsers.add_parser('modify', help='Modify components of the deployment in Kubernetes')
    modifyParser.add_argument('name', help=helpStrings['name'])
    modifyParser.add_argument('--replicas', help=helpStrings['replicas'], action='store', default='1')

    args = mainParser.parse_args()

    if args.command == 'deploy':
        deploy.main(args)
    elif args.command == 'build':
        build.main(args)
    elif args.command == 'destroy':
        destroy.main(args)
    elif args.command == 'modify':
        modify.main(args)
    else:
        mainParser.print_help()
