import click
from lantern_cli import settings
from lantern_cli import templates


@click.group()
def cli():
	"""
    \b
             * * * * * * * * * * * * * * *
             *                           * 
             *    Lantern Engine CLI     * 
             *                           *
             * * * * * * * * * * * * * * *
	\b
    This tool is for internal user
    in Lantern.tech.
    \b
    "Happy Coding!"
    """
	pass

@cli.command()
def createservice():
    """Create a new Serverless (Zappa) based microservice
        Usage:
        \n\t\t lantern-cli createservice [SERVICE_NAME]
    """
    templates.startapp(template=settings.MICROSERVICE_ZAPPA_TEMPLATE_repo)

@cli.command()
def createservice_docker():
	"""Create a new Docker Based MicroService project \n\n
	   Check the generated README file (project root) for docker instructions. \n
	   Usage:
	   \n\t\t lantern-cli createservice_docker [SERVICE_NAME]
	"""
	templates.startapp(template=settings.MICROSERVICE_DOCKER_TEMPLATE_repo)