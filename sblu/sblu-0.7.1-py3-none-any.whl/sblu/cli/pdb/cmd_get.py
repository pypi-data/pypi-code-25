from sblu.pdb import get_rcsb_pdb_stream
import urllib.error
import logging
import click

from .. import setup_for_command_line

logger = logging.getLogger(__name__)
SHORT_HELP = "Download a PDB file from the RCSB"


@click.command('get', short_help=SHORT_HELP)
@click.argument("pdb_id")
def cli(pdb_id):
    try:
        with get_rcsb_pdb_stream(pdb_id) as f, \
                open('{}.pdb'.format(pdb_id), 'wb') as f_out:
            f_out.write(f.read())
    except urllib.error.HTTPError as err:
        if err.code == 404:
            logger.error('PDB ID {} not found'.format(pdb_id))
        else:
            logger.error('Fetching PDB ID {} returned {}'.format(pdb_id, err))
    except PermissionError as err:
        logger.error('No permission to create {}.pdb'.format(pdb_id))


@click.command('pdbget', short_help=SHORT_HELP)
@click.argument("pdb_id")
@click.option("-v", "--verbose", count=True)
@click.pass_context
def standalone_cli(ctx, pdb_id, verbose):
    setup_for_command_line(verbose)
    ctx.invoke(cli, pdb_id=pdb_id)
