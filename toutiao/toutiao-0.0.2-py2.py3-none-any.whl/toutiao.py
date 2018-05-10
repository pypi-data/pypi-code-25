#! /usr/bin/env python

import click
import requests
from requests.compat import urljoin
from bs4 import BeautifulSoup
from datetime import date as datee, timedelta
from version import __version__ as version

URL = 'https://toutiao.io/'
END_POINTS = {
    'daily': '/prev/',
    'top': '/top/'
}
SELECTORS = {
    'daily': '.post .content',
    'top': '.daily > h4 > a',
    'post': '.detail, .post-tags'
}
CALLBACKS = {
    'daily': lambda node: node['data-url'],
    'top': lambda node: node['href']
}

@click.command()
@click.argument('date', default=datee.today())
@click.option('--top', is_flag=True, help='Show top3 posts for the given date')
@click.option('--verbose', '-v', is_flag=True, help='Show more information for each post')
@click.version_option(version)
def cli(date, top, verbose):
    if top and isinstance(date, datee):
        date -= timedelta(1)
    time = str(date)
    key = 'top' if top else 'daily'
    nodes = cook(urljoin(URL, END_POINTS[key] + time), key)

    click.echo('DATE: ' + time)
    if verbose or top:
        for url in [urljoin(URL, CALLBACKS[key](node)) for node in nodes]:
            post = cook_post(url)
            click.echo()
            for k, v in post.items():
                if v:
                    click.echo(k + ': ' + v)
    else:
        posts = [{'title': node.a.get_text(strip=True), 'url': urljoin(URL, node.a['href'])} for node in nodes]
        for post in posts:
            click.echo()
            click.echo(post['title'])
            click.echo(post['url'])

def cook(url, key):
    r = requests.get(url, headers={'user-agent': 'Mozilla/5.0 TouTiao/' + version})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup.select(SELECTORS[key])

def cook_post(url):
    detail, post_tag = cook(url, 'post')
    tags = [ a.get_text() for a in post_tag('a')]

    head_node = detail.select_one('.title > a')
    small = head_node.small
    if small:
        small.clear()
    title, url = head_node.get_text(strip=True), head_node['href']

    summary_node = detail.select_one('.summary')
    summary = summary_node.get_text(strip=True) if summary_node else None

    meta_node = detail.select_one('.meta')
    meta = meta_node.get_text(strip=True).replace("\n", '') if meta_node else None

    return {
        'title': title,
        'url': urljoin(URL, url),
        'from': meta,
        'summary': summary,
        'tags': ', '.join(tags)
    }

if __name__ == '__main__':
    cli()
