import click
from cookiecutter.main import cookiecutter


def startapp(template):
    """
      Create a new project based on template coockiecutter
    """
    cookiecutter(template)