# -*- coding: utf-8 -*-

from docopt import docopt
from toolz.curried import pipe, sorted, map, get
from mistune_contrib.mdrenderer import MdRenderer
from version import VERSION
import re
import mistune


def escape(text):
    return text.replace('_', "\\_").replace('*', "\\*")


def list_items(text):
    while text:
        text, type, t = MdRenderer.get_block(text)
        if type == 'l':
            yield t


def get_stars(text):
    res = re.match("\[.+\s+★(\d+)\]", text)
    if res:
        [stars] = res.groups()
        return int(stars) * -1 or 0
    return 0


class SortedMarkdown(MdRenderer):
    def link(self, link, title, text, image=False):
        r = (image and '!' or '') + '[' + escape(text) + '](' + link + ')'
        if title:
            r += '"' + title + '"'
        return r

    def text(self, text):
        return escape(text)

    def paragraph(self, text):
        return escape(text) + "\n\n"

    def autolink(self, link, is_email=False):
        return link

    def header(self, text, level, raw=None):
        return '#' * level + ' ' + text + '\n\n'

    def list(self, text, ordered=True):
        return "\n".join(
            pipe(
                list_items(text),
                sorted(key=get_stars),
                map(lambda a: (ordered and ('# ' + a) or ('* ' + a))),
                list)) + "\n\n"


class FileSystemIO(object):
    def read(self, file):
        with open(file) as f:
            return str(f.read())

    def write(self, text):
        print(text)


def run(markdown, io):
    renderer = SortedMarkdown()
    process = mistune.Markdown(renderer=renderer)
    pipe(markdown, io.read, process, io.write)


def main():
    doc = """sorted-mkdn
        Usage:
        sorted-mkdn <markdown>
        sorted-mkdn --version

        Options:
        --version        Show version.
        -h --help        Show this screen.
        """
    args = docopt(doc, version='sorted-mkdn {}'.format(VERSION))
    [markdown] = get(['<markdown>'])(args)
    IO = FileSystemIO
    run(markdown, IO())


if __name__ == '__main__':
    main()
