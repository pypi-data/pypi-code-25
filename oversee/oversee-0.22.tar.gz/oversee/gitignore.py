import os
import re
import urllib.request

import bs4
import click
import yaml
from click import ClickException

from oversee import config


file = os.path.join(os.getcwd(), '.gitignore.yaml')
if os.path.exists(file):
    with open(file) as f:
        project_gitignore = yaml.load(f)
else:
    project_gitignore = {}


def replace_lines(lines, variables):
    for i in range(len(lines)):
        pattern = '<([a-zA-Z]+)>'
        while True:
            try:
                name = re.search(pattern, lines[i]).group(1)
                lines[i] = re.sub('<{}>'.format(name), variables[name], lines[i])
            except AttributeError:
                break
    return lines


class GitIgnore:
    def __init__(self, name=None):
        self.name = name
        if name in config.gitignore:
            click.echo('Adding {} .gitignore from config!'.format(name))
            self.lines = config.gitignore[name]
            self.lines = replace_lines(self.lines, project_gitignore.get('variables', {}))
        elif name is not None:
            click.echo('Searching on GitHub for {}!'.format(name))
            self.lines = self.from_github(name)
        else:
            self.lines = []

    @staticmethod
    def from_local():
        lines = project_gitignore.get('gitignore', [])
        variables = project_gitignore.get('variables', {})
        lines = replace_lines(lines, variables)

        gitignore = GitIgnore()
        gitignore.lines = ['#### Project Specific ###', *lines]
        return gitignore

    @staticmethod
    def from_github(name):
        name = name.lower()
        name = '{}.gitignore'.format(name)
        urls = ['https://github.com/github/gitignore', 'https://github.com/github/gitignore/tree/master/Global']
        for url in urls:
            resp = urllib.request.urlopen(url)
            soup = bs4.BeautifulSoup(resp, "html.parser", from_encoding=resp.info().get_param('charset'))

            for link in soup.find_all('a', href=True):
                title = link.get('title', '')
                title = title.lower()
                if title != name:
                    continue

                source = link.get('href')
                source = 'https://raw.githubusercontent.com{}'.format(source)
                source = source.replace('/blob', '')
                click.echo('Grabbing .gitignore from {}'.format(source))

                official_gitignore = urllib.request.urlopen(source).read().decode().split('\n')
                official_gitignore = [line.strip() for line in official_gitignore]

                return official_gitignore
        else:
            raise ClickException('No .gitignore files found named {}!'.format(name))

    def extend(self, other):
        if self.lines:
            self.lines.append('\n')

        self.lines.append('### {} ###'.format(other.name))
        self.lines.extend(other.lines)

    def export(self, path):
        file = os.path.join(path, '.gitignore')
        if not os.path.exists(file):
            if not click.confirm('Create .gitignore in {}?'.format(path)):
                return
        else:
            if not click.confirm('Overwrite .gitignore in {}?'.format(path)):
                return

        with open(file, 'w') as f:
            f.write('\n'.join(self.lines))
