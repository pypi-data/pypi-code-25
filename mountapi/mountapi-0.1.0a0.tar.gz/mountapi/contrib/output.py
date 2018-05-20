import datetime
import sys


def write_stdout(msg: str, prefix_ts: bool = True) -> None:
    if prefix_ts:
        msg = f'[{datetime.datetime.now()}]: {msg}\n'

    sys.stdout.write(msg)
