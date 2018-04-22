import os

from click import echo


def multiline_input():
    echo("Enter/Paste your content. Ctrl-D to save it.")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    return '\n'.join(contents)


def add_url_kwargs(url, **kwargs):
    if not kwargs:
        return url
    url += '?'
    for k, v in kwargs.items():
        url += f'{k}={v}&'
    return url.strip('&')


def get_terminal_size(fallback=(80, 24)):
    for i in range(0, 3):
        try:
            columns, rows = os.get_terminal_size(i)
        except OSError:
            continue
        break
    else:  # set default if the loop completes which means all failed
        columns, rows = fallback
    return columns, rows
