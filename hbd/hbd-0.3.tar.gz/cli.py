"""Command line interface for Humble Bundle API."""

from pathlib import Path
import textwrap
import threading

import appdirs
import click
from tqdm import tqdm

import hbd


# Constants
############
CONFIG_DIR = Path(appdirs.user_config_dir(appname='hbd'))
SESSION_FILE = CONFIG_DIR / 'session.txt'
CACHE_DIR = Path(appdirs.user_cache_dir(appname='hbd'))
DEFAULT_OUTPUT_FORMAT = '{FileName}'
DOWNLOAD_WARNING_TIMEOUT = 5


# Command line interface
#########################

@click.group()
@click.version_option()
def cli():
    """Main entry point for CLI."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@cli.command()
@click.option('--sessionkey', help='Set current session token')
def login(sessionkey: str):
    """Log user into Humble Bundle site."""
    if sessionkey:
        SESSION_FILE.write_text(sessionkey)
    else:
        hb = hbd.HumbleDownloader()
        # TODO: Do login, handle CAPTCHA
        hb.login('user', 'pass')


@cli.command()
@click.pass_context
def ls(ctx: click.Context):  # pylint: disable=invalid-name
    """Display all purchases."""
    session_key = get_session_or_quit(ctx)
    humble = hbd.HumbleDownloader(session_key=session_key, cache_dir=CACHE_DIR)
    keys = humble.get_purchase_list()
    for key in keys:
        purchase_details = humble.get_purchase(key)
        # Single line broken up into multiple strings for readability
        print(f'{purchase_details.product.human_name} '
              f'({purchase_details.product.machine_name})')


@cli.command()
@click.argument('machine_name')
@click.pass_context
def show(ctx: click.Context, machine_name: str):
    """Display information on a single purchase."""
    session_key = get_session_or_quit(ctx)
    humble = hbd.HumbleDownloader(session_key=session_key, cache_dir=CACHE_DIR)
    purchase_key = find_key_with_warning(humble, machine_name)
    if not purchase_key:
        print(f'{machine_name} not found')
        ctx.exit(1)
    purchase_info = humble.get_purchase(purchase_key)
    print_purchase_info(purchase_info)


@cli.command()
@click.argument('machine_name')
@click.option('--verify/--no-verify', 'verify_download', default=False)
@click.option('--dryrun/--no-dryrun', default=False)
@click.option('--output', 'output_format', default=DEFAULT_OUTPUT_FORMAT)
@click.pass_context
def download(ctx: click.Context,  # pylint: disable=too-many-arguments
             machine_name: str, verify_download: bool, dryrun: bool,
             output_format: str,
             retry_expired_gamekey: bool = True):
    """Display information on a single purchase.

    retry_expired_gamekey: If True attempt to redownload purchase data and
        download again.
    """
    session_key = get_session_or_quit(ctx)
    humble = hbd.HumbleDownloader(session_key=session_key, cache_dir=CACHE_DIR)
    purchase_key = find_key_with_warning(humble, machine_name)
    if not purchase_key:
        print(f'{machine_name} not found')
        ctx.exit(1)
    purchase = humble.get_purchase(purchase_key)
    downloads = purchase.find_downloads(output_format=output_format)
    try:
        for output_path, download_struct in downloads.items():
            if not output_path.exists():
                click.echo(f"Downloading {output_path}:")
                if not dryrun:
                    download_with_progress(download_struct, output_path, verify_download)
            else:
                click.echo(f"Skipping existing file {output_path}")
    except EOFError:
        # Caused by gamekey on download expired, redownload to fix
        # TODO: Error logging/print on verbose mode
        if retry_expired_gamekey:
            click.echo('Download failed, clearing cache and retrying')
            humble.clear_purchase_cache(purchase_key)
            ctx.forward(download, retry_expired_gamekey=False)
        else:
            click.echo('Unable to download file')

    if dryrun:
        click.echo("Dry run, no files downloaded")


@cli.command()
@click.argument('machine_name')
@click.option('--output', 'output_format', default=DEFAULT_OUTPUT_FORMAT)
@click.pass_context
def verify(ctx: click.Context, machine_name: str, output_format: str):
    """Check downloaded files against MD5 hashes from Humble Bundle."""
    session_key = get_session_or_quit(ctx)
    humble = hbd.HumbleDownloader(session_key=session_key, cache_dir=CACHE_DIR)
    purchase_key = find_key_with_warning(humble, machine_name)
    if not purchase_key:
        print(f'{machine_name} not found')
        ctx.exit(1)
    purchase = humble.get_purchase(purchase_key)
    downloads = purchase.find_downloads(output_format=output_format)
    missing_text = click.style("MISSING", fg='red')
    failure_text = click.style("FAILURE", fg='red')
    for output_path, download_struct in downloads.items():
        if output_path.exists():
            if hbd.verify_download(download_struct, output_path):
                click.echo(f"{output_path}: OK")
            else:
                click.echo(f"{output_path}: " + failure_text)
        else:
            click.echo(f"{output_path}: " + missing_text)


# Support functions
####################

def print_purchase_info(purchase: hbd.Purchase):
    """Print information about whole purchase."""
    click.echo(textwrap.dedent(f'''\
        Product: {purchase.product.human_name}
        Internal name: {purchase.product.machine_name}
        Purchase amount: {purchase.amount_spent}\n'''))
    for subproduct in purchase.subproducts:
        print_subproduct_info(subproduct)
    total_mb = purchase.total_size / 1024**2
    num_files = len(purchase.find_downloads())
    click.echo(f"\nTotal download size: {total_mb:.2f}MB in {num_files} files")


def print_subproduct_info(subproduct: hbd.Subproduct):
    """Print information about a specific item to screen."""
    download_details = ""
    total_size = 0
    for d in subproduct.downloads:
        for struct in d.download_struct:
            # Ignore streams, asmjs, etc.
            if struct.url:
                details = ' ' * 16 + \
                    f'{struct.file_name} ' \
                    f'({d.platform}, {struct.name}) - ' \
                    f'{struct.human_size}\n'
                download_details += details
                total_size += struct.file_size
            else:
                details = ' ' * 16 + f'{d.machine_name} ({d.platform}) - N/A'
    download_details = download_details.rstrip()

    if total_size > 0:
        total_size_human = f'{total_size // 1024**2} MB'
        download_summary = f'Downloads (' \
            f'{total_size_human} in {len(subproduct.downloads)} files):\n' \
            f'{download_details}'
    else:
        download_summary = 'No downloads available'
    print(textwrap.dedent(f'''\
        Subproduct: {subproduct.human_name}
            Machine name: {subproduct.machine_name}
            Publisher: {subproduct.payee["human_name"]}
            URL: {subproduct.url}
            {download_summary}'''))


def download_with_progress(download_struct: hbd.DownloadStruct,
                           output_path: Path,
                           verify_download: bool):
    """Downloads a file printing progress information."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(output_path.name + '.hbdownload')
    with tqdm(total=download_struct.file_size, unit='B',
              unit_scale=True, unit_divisor=1024) as pbar:
        hbd.download_file(download_struct, temp_path,
                          progress_callback=pbar.update)
    if verify_download:
        click.echo("Verifying download...")
        if hbd.verify_download(download_struct, temp_path):
            temp_path.rename(output_path)
        else:
            click.secho("Download failed", fg='red')
            temp_path.unlink()
    else:
        temp_path.rename(output_path)


def get_session_or_quit(ctx: click.Context) -> str:
    """Returns session key or if not available quit the program."""
    if not SESSION_FILE.exists():
        click.echo('You must log in before using that command')
        ctx.exit(1)
    return SESSION_FILE.read_text()


def find_key_with_warning(humble: hbd.HumbleDownloader, name: str) -> str:
    """find_key_from_name may take a while, show warning if it takes too long."""
    timer = threading.Timer(DOWNLOAD_WARNING_TIMEOUT, lambda: click.echo(
        'Downloading bundle information, may take a while for large collections...'))
    timer.start()
    purchase_key = humble.find_key_from_name(name)
    timer.cancel()
    return purchase_key
