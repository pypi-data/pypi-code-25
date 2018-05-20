import importlib

from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Starts the GRPC server"

    default_port = "55001"

    def add_arguments(self, parser):
        parser.add_argument(
            "project", nargs="1",
            help="Django project settings path"
        )
        parser.add_argument(
            "port", nargs="?",
            help="Optional port number"
        )
        parser.add_argument(
            "--workers", dest="max_workers",
            help="Number of maximum worker threads"
        )

    def handle(self, *args, **options):
        project_module = importlib.import_module(".".join([options["project"], "grpc"]))
        print(project_module.settings)
        if not options.get("port"):
            self.port = self.default_port
        else:
            self.port = options["port"]
            if not self.port.isdigit():
                raise CommandError("{} is not a valid port number".format(self.port))