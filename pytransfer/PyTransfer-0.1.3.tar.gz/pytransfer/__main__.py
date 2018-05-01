import argparse
import sys
from multiprocessing import freeze_support, Pool, Lock
from tqdm import tqdm
from .utils import get_service_provider_class

from pytransfer.utils import upload_file


def get_args(args):
    arg = argparse.ArgumentParser(description="App that simplifies usage of file hosting services (currently only https://transfer.sh)")
    arg.add_argument(
        'filename',
        nargs='*',
        default=(),
        help='Name of file you want to upload'
    )

    return arg.parse_args(args)


def init_child(write_lock):
    """
    Provide tqdm with the lock from the parent app.
    This is necessary on Windows to avoid racing conditions.
    """
    tqdm.set_lock(write_lock)


def main():
    args = get_args(sys.argv[1:])

    # Prepare files
    files = []
    i = 0
    for file in args.filename:
        files.append({
            'path': file,
            'order': i
        })
        i += 1

    freeze_support()
    write_lock = Lock()
    uploaded_files_links = Pool(len(args.filename), initializer=init_child, initargs=(write_lock,)).map(upload_file, files)

    # Fix cursor position. It isn't good solution, but it works
    for i in range(len(args.filename) + 1):
        print()

    service_provider = get_service_provider_class()
    try:
        service_provider.print_post_upload_message(uploaded_files_links)
    except AttributeError:
        pass


if __name__ == '__main__':
    main()
