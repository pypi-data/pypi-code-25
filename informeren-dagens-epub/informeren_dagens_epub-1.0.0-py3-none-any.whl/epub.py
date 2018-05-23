#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from datetime import datetime, timedelta
import getopt
import json
import logging
import os
import re
import shutil
import sqlite3
import sys
import tempfile

from bs4 import BeautifulSoup
import requests

from .version import VERSION


class EPUBExtractor():
    """Extracting EPUB versions of Danish daily Information."""

    BASE_URL = 'https://www.information.dk'
    REQUEST_HEADERS = {
        'User-Agent': (
            'Dagens Avis som EPUB '
            '(https://gitlab.com/gorgonzola/informeren-dagens-epub)'
        ),
    }

    def __init__(self, cookies, publication_date):
        self.logger = logging.getLogger('informeren_dagens_epub')
        self.logger.setLevel(logging.DEBUG)
        log = logging.StreamHandler()
        self.logger.addHandler(log)
        self.cookies = cookies
        self.publication_date = publication_date
        self.root = os.path.dirname(__file__)

    def extract_toc(self):
        """Extract the table of contents."""
        self.logger.debug('Extracting TOC for %s...' % self.publication_date)

        # Fetch webpage and set up a parser.
        html = requests.get(
            '{}/dagensavis/{}'.format(
                self.BASE_URL,
                self.publication_date
            ),
            cookies=self.cookies,
            headers=self.REQUEST_HEADERS
        ).text
        soup = BeautifulSoup(html, 'html.parser')

        # Get the title.
        title = soup.find('header', class_='title').string.strip()

        # Get the articles.
        articles = []
        for adata in soup.find_all('div', class_='node-article'):
            path = adata.find('a')['href']
            articles.append({
                'title': adata.find('a').string.strip(),
                'path': path,
                'slug': path.split('/')[-1],
                'description': adata.find(
                    class_='field-name-field-web-underrubrik').string.strip(),
            })

        return title, articles

    def extract_author_name(self, author):
        """Extract the author name from an author name element."""
        self.logger.debug('Extracting author name...')

        if author.find('div', class_='field-name-title'):
            return author.find('div', class_='field-name-title').string.strip()
        return author.find('a').string.strip()

    def extract_article(self, article):
        """Extract full article data."""
        self.logger.debug(
            'Extracting article from <%s>...' % article.get('path')
        )

        # Fetch webpage and set up a parser.
        html = requests.get(
            '{}{}'.format(
                self.BASE_URL,
                article.get('path')
            ),
            cookies=self.cookies,
            headers=self.REQUEST_HEADERS
        ).text
        soup = BeautifulSoup(html, 'html.parser')

        # Get the authors.
        authors = [
            self.extract_author_name(a) for a in
            soup.find('ul', class_='byline').find_all('li')
        ]

        # Get the title.
        title = soup.find('article').find('header').find('h1').string.strip()

        # Get the intro.
        intro = soup.find(class_='field-name-field-underrubrik')
        if intro:
            intro = intro.string.strip()

        # Get the photo.
        photo = soup.find(class_='field-name-top-image')
        if photo:
            photo = photo.find('img')
        if photo:
            photo = photo['src']

        # Get the estimated reading time.
        reading_time = soup.find(
            class_='c-node-premium-marker-title__reading-time'
        )
        if reading_time:
            reading_time = reading_time.string.strip()

        # Get the content and remove unwanted elements.
        content = soup.find(class_='field-name-body')
        for item in content.find_all(class_='c-newsletter-signup-box'):
            item.decompose()
        for item in content.find_all(class_='view-mode-read_this_inline_teaser'):
            item.decompose()

        article.update({
            'authors': authors,
            'reading_time': reading_time,
            'title': title,
            'intro': intro,
            'photo': photo,
            'content': content,
        })

        return article

    def build_metadata(self, title, articles):
        """Build a metadata document for the EPUB."""
        self.logger.debug('Building metadata...')

        # Open the metadata template.
        with open('{}/template/EPUB/package.opf'.format(self.root)) as f:
            soup = BeautifulSoup(f.read(), 'xml')

        # Set the identifier.
        soup.find(
            'identifier'
        ).string = 'gorgonzola-informeren-dagens-{}'.format(
            self.publication_date
        )

        # Set the title.
        soup.find('title').string = 'Information – {}'.format(title)

        # Set the date modified.
        now = datetime.utcnow()
        now = now - timedelta(microseconds=now.microsecond)
        soup.find('meta').string = now.isoformat() + 'Z'

        # Get lists and the item templates.
        manifest = soup.find('manifest')
        spine = soup.find('spine')
        item_template = copy.copy(soup.find('item'))
        del item_template['properties']
        itemref_template = soup.find('itemref')

        # Insert frontpage references.
        item = copy.copy(item_template)
        itemref = copy.copy(itemref_template)

        # Insert item.
        item['href'] = 'xhtml/frontpage.xhtml'
        item['id'] = 'frontpage'
        manifest.insert(0, item)

        # Insert reference.
        itemref['idref'] = 'frontpage'
        spine.insert(0, itemref)

        # Insert items and references.
        for article in articles:
            item = copy.copy(item_template)
            itemref = copy.copy(itemref_template)

            # Insert item.
            item['href'] = 'xhtml/{}.xhtml'.format(article.get('slug'))
            item['id'] = article.get('slug')
            manifest.append(item)

            # Insert reference.
            itemref['idref'] = article.get('slug')
            spine.append(itemref)

        return soup

    def build_navigation(self, title, articles):
        """Build the navigation for the EPUB."""
        self.logger.debug('Building navigation...')

        # Open the navigation template.
        with open('{}/template/EPUB/xhtml/nav.xhtml'.format(self.root)) as f:
            soup = BeautifulSoup(f.read(), 'xml')

        # Set the title.
        soup.find('title').string = 'Information – {}'.format(title)
        soup.find('h1').string = 'Information – {}'.format(title)

        # Get navigation list and the item template.
        navigation = soup.find('ol')
        item_template = soup.find('li')

        # Insert the frontpage reference.
        item = copy.copy(item_template)
        item.find('a')['href'] = 'frontpage.xhtml'
        item.find('a').string = 'Forside'
        item['id'] = 'frontpage'
        navigation.insert(0, item)

        # Insert items and references.
        for article in articles:
            item = copy.copy(item_template)

            # Insert item.
            item.find('a')['href'] = '{}.xhtml'.format(article.get('slug'))
            item.find('a').string = article.get('title')
            item['id'] = article.get('slug')
            navigation.append(item)

        return soup

    def build_article(self, article, neighbour_slugs=(None, None)):
        """Build an article document for the EPUB."""
        self.logger.debug('Building article "%s"...' % article.get('title'))

        # Extract article data.
        article = self.extract_article(article)

        # Get the article template.
        with open(
            '{}/template/EPUB/xhtml/article.xhtml'.format(self.root)
        ) as f:
            soup = BeautifulSoup(f.read(), 'xml')

        # Set article meta data.
        soup.find('title').string = article.get('title')
        soup.find('h1').string = article.get('title')
        meta = soup.find('ul', class_='meta')
        meta_item_template = meta.find('li').extract()
        authors = copy.copy(meta_item_template)
        authors.string = 'Af: {}'.format(', '.join(article.get('authors')))
        meta.append(authors)
        if article.get('reading_time'):
            reading_time = copy.copy(meta_item_template)
            reading_time.string = article.get('reading_time')
            meta.append(reading_time)
        www = copy.copy(meta_item_template)
        www.clear()
        www_link = soup.new_tag(
            'a',
            href='{}{}'.format(
                self.BASE_URL,
                article.get('path')
            ),
        )
        www_link.string = 'www'
        www.append(www_link)
        meta.append(www)

        prev_slug, next_slug = neighbour_slugs
        if prev_slug:
            prev = copy.copy(meta_item_template)
            prev.clear()
            prev_link = soup.new_tag(
                'a',
                href='{}.xhtml'.format(
                    prev_slug
                ),
            )
            prev_link.string = '«'
            prev.append(prev_link)
            meta.append(prev)

        if next_slug:
            nxt = copy.copy(meta_item_template)
            nxt.clear()
            nxt_link = soup.new_tag(
                'a',
                href='{}.xhtml'.format(
                    next_slug
                ),
            )
            nxt_link.string = '»'
            nxt.append(nxt_link)
            meta.append(nxt)

        # Set the article intro.
        intro_item = soup.find(class_='intro')
        if article.get('intro'):
            intro_item.string = article.get('intro')
        else:
            intro_item.decompose()

        # Set the article photo.
        photo_item = soup.find(class_='photo')
        if article.get('photo'):
            with open('{}/EPUB/img/{}.jpg'.format(
                self.temp_dir,
                article.get('slug')
            ), 'wb') as f:
                f.write(
                    requests.get(
                        article.get('photo'),
                        headers=self.REQUEST_HEADERS
                    ).content
                )
            photo_item.find('img')['src'] = '../img/{}.jpg'.format(
                article.get('slug')
            )
        else:
            photo_item.decompose()

        # Set article content.
        content = soup.find('p', class_='body')
        content.clear()
        content.append(article.get('content'))

        # Download inline images.
        idx = 0
        for i in content.find_all('img'):
            idx += 1
            self.logger.debug('Replacing inline image #{}...'.format(idx))
            with open('{}/EPUB/img/{}-{}.jpg'.format(
                self.temp_dir,
                article.get('slug'),
                idx
            ), 'wb') as f:
                f.write(
                    requests.get(
                        i['src'],
                        headers=self.REQUEST_HEADERS
                    ).content
                )
            i['src'] = '../img/{}-{}.jpg'.format(
                article.get('slug'),
                idx
            )

        # Fix foto credits for inline images.
        for c in soup.select(
            '.media-inline-full .field-name-field-contributor .field-item'
        ):
            c.string = 'Foto: ' + c.string.strip()



        return soup

    def build_frontpage(self, title):
        """Build a frontpage document for the EPUB."""
        self.logger.debug('Building the frontpage...')

        # Get the frontpage template.
        with open(
            '{}/template/EPUB/xhtml/frontpage.xhtml'.format(self.root)
        ) as f:
            soup = BeautifulSoup(f.read(), 'xml')

        # Check whether date is recent enough for an image of the front page of
        # the printed paper to be available.
        age = datetime.now() - datetime(
            int(self.publication_date[6:10]),
            int(self.publication_date[3:5]),
            int(self.publication_date[0:2])
        )
        if age.days > 28:
            logger.debug('Frontpage image not available.')
            soup.find('div').decompose()
            soup.find('h2').string = title
        else:
            self.logger.debug('Fetching frontpage image...')

            soup.find('h1').decompose()
            soup.find('h2').decompose()
            soup.find('img')['src'] = '../img/frontpage.jpg'
            soup.find('img')['alt'] = 'Information – {}'.format(title)

            with open('{}/EPUB/img/frontpage.jpg'.format(
                self.temp_dir
            ), 'wb') as f:
                f.write(
                        requests.get(
                            '{}/sites/information.dk/files/styles/todays_paper/'
                            'public/printforsider/{}.jpg'.format(
                                self.BASE_URL,
                                self.publication_date[0:2]
                            ),
                            headers=self.REQUEST_HEADERS
                        ).content
                )

        return soup

    def build_epub(self):
        """Build an EPUB of the newspaper from the date."""
        self.logger.debug('Building EPUB for %s...' % self.publication_date)

        # Create a temporary directory for the EPUB files.
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            # Get the title and table of contents.
            title, articles = self.extract_toc()

            # Copy some of the template files.
            shutil.copy(
                '{}/template/mimetype'.format(self.root),
                self.temp_dir
            )
            shutil.copytree(
                '{}/template/META-INF'.format(self.root),
                '{}/META-INF'.format(self.temp_dir)
            )

            # Create directory structure for custom files.
            os.mkdir('{}/EPUB'.format(self.temp_dir))
            os.mkdir('{}/EPUB/xhtml'.format(self.temp_dir))
            os.mkdir('{}/EPUB/img'.format(self.temp_dir))

            # Write the frontpage.
            with open('{}/EPUB/xhtml/frontpage.xhtml'.format(
                self.temp_dir
            ), 'w') as f:
                f.write(self.build_frontpage(title).prettify())

            # Write the metadata file.
            with open('{}/EPUB/package.opf'.format(self.temp_dir), 'w') as f:
                f.write(self.build_metadata(title, articles).prettify())

            # Write the navigation.
            with open('{}/EPUB/xhtml/nav.xhtml'.format(
                self.temp_dir
            ), 'w') as f:
                f.write(self.build_navigation(title, articles).prettify())

            # Write the article files.
            for i in range(len(articles)):
                # Get the article.
                article = articles[i]

                # Get paths to neighbour articles.
                prev_slug = articles[i - 1].get('slug') if i > 0 else None
                next_slug = (
                    articles[i + 1].get('slug')
                    if i < len(articles) - 1
                    else None
                )

                # Build the article file.
                with open('{}/EPUB/xhtml/{}.xhtml'.format(
                    self.temp_dir,
                    article.get('slug'),
                ), 'w') as f:
                    f.write(self.build_article(
                        article,
                        (prev_slug, next_slug)
                    ).prettify())

            # Create a zip archive of the EPUB directory and clear the local
            # reference before it's destroyed.
            shutil.make_archive(
                './{}'.format(self.publication_date),
                'zip', self.temp_dir
            )
            self.temp_dir = None

        # Rename .zip file to .epub
        shutil.move(
            './{}.zip'.format(self.publication_date),
            './{}.epub'.format(self.publication_date)
        )

        self.logger.debug('EPUB ready :)')

def extract_firefox_cookies(path):
    """
    Extract relevant cookies from Firefox cookie storage.

    `path` should point to the `cookies.sqlite` in the Firefox user profile."""
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(
        'SELECT name, value FROM moz_cookies WHERE baseDomain LIKE '
        '\'%information.dk\' AND (name LIKE \'SSESS%\' OR '
        'name=\'CHOCOLATECHIPSSL\');'
    )
    return {name: value for name, value in cursor.fetchall()}

def usage():
    print("""Informeren – Today's EPUB (version {})

Usage: informeren-epub [options]

Available options are:

-f, --firefox-cookie-path <path>    Path to the `cookies.sqlite` file in your
                                    Firefox profile.
-j, --json-cookie-path <path>       Path to a JSON cookie file (e.g. generated
                                    with the combination of the `-f` and
                                    `-P flags.).
-d, --date <dd-mm-yyyy>             Date of the newspaper issue to get an EPUB
                                    for. The format may seem a bit odd, but it
                                    follows the format of the paths for the web
                                    version of the newspaper.
-P, --print-cookies                 Print the loaded cookies instead of
                                    generating the EPUB file. This is useful
                                    if you want to generate a JSON cookie file
                                    that can be exported to another computer
                                    without a Firefox that is logged in to
                                    information.dk with an active subscription.
-h, --help                          Show this message.
""".format(VERSION))

def main():
    """The main script."""
    # Read command line arguments.
    argv = sys.argv[1:]

    # Try parsing the arguments.
    try:
        opts, args = getopt.getopt(argv, 'f:j:d:Ph', [
            'firefox-cookie-path=',
            'json-cookie-path=',
            'date=',
            'print-cookies',
            'help',
        ])
    except getopt.GetoptError:
        print('Invalid arguments :(')
        exit(1)

    # Extract arguments.
    firefox_cookie_path = None
    json_cookie_path = None
    publication_date = None
    print_cookies = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            exit()
        if opt in ('-f', '--firefox-cookie-path'):
            firefox_cookie_path = arg
        if opt in ('-j', '--json-cookie-path'):
            json_cookie_path = arg
        elif opt in ('-d', '--date'):
            publication_date = arg
        elif opt in ('-P', '--print-cookies'):
            print_cookies = True

    if firefox_cookie_path is None and json_cookie_path is None:
        print(
            'You need to provide the path to your Firefox cookie file or a '
            'path to a JSON cookie file, in order to be able to extract full '
            'articles behind the paywall with your authentication cookies.'
            '\n\n'
            'The path to the Firefox cookie file can be provided via the '
            '`-f/--firefox-cookie-path` option. Usually, the path is '
            'something like `~/.mozilla/firefox/your.profile/cookies.sqlite`.'
            '\n\n'
            'The path to a JSON cookie file can be provided via the '
            '`-j/--json-cookie-file` option. This can be located anywhere you '
            'want and should contain a JSON object with 2 key-value pairs '
            'representing the cookies from the `information.dk` domain '
            'named `SSESS[something]` and `CHOCOLATECHIPSSL` and their values.'
            '\n\n'
            'A JSON cookie file can be generated from the Firefox cookie '
            'file, by providing the `-P/--print-cookies` argument along with '
            'the Firefox cookie option. This will print the cookies in JSON, '
            'which you can then pipe into a JSON cookie file. This is '
            'useful if you want to run the EPUB extractor from another '
            'computer than the one with your browser (e.g. from a server, '
            'having your browser on your desktop PC). Then simply generate a '
            'JSON cookie file on the browser computer and transfer it to the '
            'other computer.'

        )
        exit(2)

    if publication_date is None:
        publication_date = datetime.now().strftime('%d-%m-%Y')

    if re.match('^\d{2}-\d{1,2}-\d{4}$', publication_date) is None:
        print(
            'The provided date (`-d/--date`) is invalid. The format must be '
            '`dd-mm-yyyy`, e.g. `06-05-1945` for May 6th 1945.'
        )
        exit(3)

    # Get Cookies from Firefox cookie storage.
    if firefox_cookie_path:
        cookies = extract_firefox_cookies(firefox_cookie_path)
    # Get cookies from JSON file.
    else:
        with open(json_cookie_path) as f:
            cookies = json.loads(f.read())

    # Check that both of the required cookies are present.
    cookie_names = cookies.keys()
    if not 'CHOCOLATECHIPSSL' in cookie_names:
        print(
            'The cookie called `CHOCOLATECHIPSSL` was not found in the '
            'provided cookies. This is required to get behind the paywall.'
        )
        exit(4)
    cookie_names = [n[:5] for n in cookie_names]
    if not 'SSESS' in cookie_names:
        print(
            'The cookie called `SSESS[something]` was not found in the '
            'provided cookies. This is required to get behind the paywall.'
        )
        exit(4)


    # Print cookies if requested.
    if print_cookies:
        print(json.dumps(cookies))
        exit()

    # Build the EPUB.
    EPUBExtractor(cookies, publication_date).build_epub()

if __name__ == '__main__':
    main()
