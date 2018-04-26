"""
the main mimir cli click module
"""
import click
from mimir_cli.globals import (
    __version__
)
from mimir_cli.strings import (
    AUTH_SUCCESS,
    EMAIL_HELP,
    EMAIL_PROMPT,
    ERR_INVALID_CRED,
    ERR_NOT_AUTH,
    LOGOUT_SUCCESS,
    PW_HELP
)
from mimir_cli.utils.auth import (
    login_to_mimir,
    logout_of_mimir,
    read_credentials
)
from mimir_cli.utils.projects import (
    get_projects_list,
    prompt_for_project,
    print_projects
)
from mimir_cli.utils.submit import (
    submit_to_mimir
)


@click.group()
def cli():
    """Mimir Classroom CLI"""
    pass


@cli.command()
def version():
    """Print version info"""
    click.echo('mimir_cli version {version}'.format(version=__version__))


@cli.command()
@click.option('-e', '--email', help=EMAIL_HELP, prompt=EMAIL_PROMPT)
@click.option('-p', '--password', help=PW_HELP, prompt=True, hide_input=True)
def login(email, password):
    """Log In to Mimir Classroom"""
    logged_in = login_to_mimir(email, password)
    if logged_in:
        click.echo(AUTH_SUCCESS)
        return True
    click.echo(ERR_INVALID_CRED)
    return False


@cli.command()
def logout():
    """Log Out of Mimir Classroom"""
    logout_of_mimir()
    click.echo(LOGOUT_SUCCESS)


@cli.group()
def project():
    """Project related commands"""
    pass


@project.command()
@click.option(
    '--path',
    help='the file or directory to submit',
    prompt=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True
    )
)
@click.option(
    '--project_id',
    help='the project id on Mimir Classroom',
    type=click.UUID
)
def submit(path, project_id):
    """submit project command"""
    credentials = read_credentials()
    if credentials and 'authToken' in credentials:
        click.echo(path)
        if not project_id:
            projects = get_projects_list(credentials)
            selected_project = prompt_for_project(projects)
            project_id = selected_project['id']
        submit_to_mimir(path, project_id, credentials)
    else:
        click.echo(ERR_NOT_AUTH)


@project.command()
@click.option('-l', '--limit', default=20, help='maximum number of projects to show')
def ls(limit):
    """list open projects"""
    credentials = read_credentials()
    if credentials and 'authToken' in credentials:
        projects = get_projects_list(credentials)[:limit]
        print_projects(projects)
    else:
        click.echo(ERR_NOT_AUTH)


if __name__ == '__main__':
    cli()
