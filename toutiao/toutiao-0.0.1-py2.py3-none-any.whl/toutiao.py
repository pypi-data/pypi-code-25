#! /usr/bin/env python

import click
import requests
from bs4 import BeautifulSoup
from datetime import date as datee, timedelta
from version import __version__ as version

URLS = {
    'daily': 'https://toutiao.io/prev/',
    'top': 'https://toutiao.io/top/'
}
SELECTORS = {
    'daily': '.post .title > a',
    'top': '.daily > h4 > a'
}

@click.command()
@click.argument('date', default=datee.today())
@click.option('--top', is_flag=True, help='Show top3 posts for the given date')
@click.version_option(version)
def cli(date, top):
    if top and isinstance(date, datee):
        date -= timedelta(1)
    time = str(date)
    key = 'top' if top else 'daily'

    r = requests.get(URLS[key] + time, headers={'user-agent': 'Mozilla/5.0 TouTiao/' + version})
    soup = BeautifulSoup(r.text, 'html.parser')
    posts = soup.select(SELECTORS[key])
    titles = [post.get_text() for post in posts]

    click.echo('DATE: ' + time)
    click.echo()
    for title in titles:
        click.echo(title)

if __name__ == '__main__':
    cli()
