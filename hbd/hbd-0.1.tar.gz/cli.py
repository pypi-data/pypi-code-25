"""Command line interface for Humble Bundle API."""

import os
from pathlib import Path
import textwrap
from typing import Dict

import appdirs
import click
from tqdm import tqdm

import hbd


# Constants
############
CONFIG_DIR = Path(appdirs.user_config_dir(appname='hbd'))
SESSION_FILE = CONFIG_DIR / 'session.txt'
CACHE_DIR = Path(appdirs.user_cache_dir(appname='hbd'))


# Command line interface
#########################

@click.group()
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
def ls():
    """Display all purchases."""
    # TODO: Handle no session file
    # TODO: Show warning about downloading all JSON
    hb = hbd.HumbleDownloader(session_key=SESSION_FILE.read_text(),
                              cache_dir=CACHE_DIR)
    keys = hb.get_purchase_list()
    for key in keys:
        purchase_details = hb.get_purchase(key)
        # Single line broken up into multiple strings for readability
        print(f'{purchase_details.product.human_name} '
              f'({purchase_details.product.machine_name})')


@cli.command()
@click.argument('machine_name')
def show(machine_name: str):
    """Display information on a single purchase."""
    hb = hbd.HumbleDownloader(session_key=SESSION_FILE.read_text(),
                              cache_dir=CACHE_DIR)
    # TODO: Handle name not found
    key = hb.find_key_from_name(machine_name)
    purchase_info = hb.get_purchase(key)
    print_purchase_info(purchase_info)


@cli.command()
@click.argument('machine_name')
@click.option('--verify/--no-verify', default=False)
def download(machine_name: str, verify_download: bool):
    """Display information on a single purchase."""
    hb = hbd.HumbleDownloader(session_key=SESSION_FILE.read_text(),
                              cache_dir=CACHE_DIR)
    # TODO: Handle name not found
    purchase = hb.get_purchase(hb.find_key_from_name(machine_name))
    downloads = find_downloads(purchase)
    for output_path, download_struct in downloads.items():
        if not output_path.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Downloading {output_path}:")
            with tqdm(total=download_struct.file_size,
                      unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                hbd.download_file(download_struct, output_path,
                                  progress_callback=pbar.update)
            if verify_download:
                print("Verifying download...")
                if not hbd.verify_download(download_struct, output_path):
                    print("Download failed")
                    output_path.unlink()
        else:
            print(f"Skipping existing file", output_path)


@cli.command()
@click.argument('machine_name')
def verify(machine_name: str):
    """Check downloaded files against MD5 hashes from Humble Bundle."""
    hb = hbd.HumbleDownloader(session_key=SESSION_FILE.read_text(),
                              cache_dir=CACHE_DIR)
    # TODO: Handle name not found
    purchase = hb.get_purchase(hb.find_key_from_name(machine_name))
    downloads = find_downloads(purchase)
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
    print(textwrap.dedent(f'''\
        Product: {purchase.product.human_name}
        Internal name: {purchase.product.machine_name}
        Purchase amount: {purchase.amount_spent}\n'''))
    for subproduct in purchase.subproducts:
        print_subproduct_info(subproduct)


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
        # TODO: human-readable filesize library?
        total_size_human = f'{total_size // 1024**2} MB'
        download_summary = f'Downloads (' \
            f'{total_size_human} in {len(subproduct.downloads)}) files:\n' \
            f'{download_details}'
    else:
        download_summary = 'No downloads available'
    print(textwrap.dedent(f'''\
        Subproduct: {subproduct.human_name}
            Machine name: {subproduct.machine_name}
            Publisher: {subproduct.payee["human_name"]}
            URL: {subproduct.url}
            {download_summary}'''))


def find_downloads(purchase: hbd.Purchase) \
        -> Dict[os.PathLike, hbd.DownloadStruct]:
    """Extracts all possible downloads from a Purchase."""
    # TODO: Filters for platform, type, etc.
    downloads = {}
    for subproduct in purchase.subproducts:
        for subdownload in subproduct.downloads:
            # asmjs platform has no downloads (officially)
            if subdownload.platform != 'asmjs':
                for download_struct in subdownload.download_struct:
                    subproduct_path = Path(purchase.product.machine_name,
                                           subproduct.machine_name)
                    file_name = download_struct.file_name
                    output_path = subproduct_path / file_name
                    downloads[output_path] = download_struct
    return downloads
