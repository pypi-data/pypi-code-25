# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
from __future__ import print_function

import re
import time
import unicodedata

from six.moves.urllib.parse import urlencode
from six import text_type, string_types

from .. import find_re, strip_tags, decode_html
from .. import cache


from . siteparser import SiteParser
from . import duckduckgo
from ..utils import datetime
from ..geo import normalize_country_name


def prepare_url(url, data=None, headers=cache.DEFAULT_HEADERS, timeout=cache.cache_timeout, valid=None, unicode=False):
    headers = headers.copy()
    # https://webapps.stackexchange.com/questions/11003/how-can-i-disable-reconfigure-imdbs-automatic-geo-location-so-it-does-not-defau
    headers['X-Forwarded-For'] = '72.21.206.80'
    return url, data, headers, timeout, unicode

def read_url(url, data=None, headers=cache.DEFAULT_HEADERS, timeout=cache.cache_timeout, valid=None, unicode=False):
    url, data, headers, timeout, unicode = prepare_url(url, data, headers, timeout, valid, unicode)
    return cache.read_url(url, data, headers, timeout, unicode=unicode)

def delete_url(url, data=None, headers=cache.DEFAULT_HEADERS):
    url, data, headers, timeout, unicode = prepare_url(url, data, headers)
    cache.store.delete(url, data, headers)

def get_url(id):
    return "http://www.imdb.com/title/tt%s/" % id


def reference_section(id):
    return {
        'page': 'reference',
        're': [
            '<h4 name="{id}" id="{id}".*?<table(.*?)</table>'.format(id=id),
            '<a href="/name/.*?>(.*?)</a>'
        ],
        'type': 'list'
    }


def zebra_list(label, more=None):
    conditions = {
        'page': 'reference',
        're': [
            '_label">' + label + '</td>.*?<ul(.*?)</ul>',
            '<li.*?>(.*?)</li>'
        ],
        'type': 'list',
    }
    if more:
        conditions['re'] += more
    return conditions

def zebra_table(label, more=None, type='string'):
    conditions = {
        'page': 'reference',
        're': [
            '_label">' + label + '</td>.*?<td>(.*?)</td>',
        ],
        'type': type,
    }
    if more:
        conditions['re'] += more
    return conditions

def parse_aspectratio(value):
    r = value
    if ':' in value:
        r = value.split(':')
        n = r[0]
        d = r[1].strip().split(' ')[0]
        try:
            value = str(float(n) / float(d))
        except:
            print('failed to parse aspect: %s' % value)
    else:
        value = '.'.join(value.strip().split('.')[:2])
    return value

'''
'posterIds': {
    'page': 'posters',
    're': '/unknown-thumbnail/media/rm(.*?)/tt',
    'type': 'list'
},
'''

class Imdb(SiteParser):
    '''
    >>> Imdb('0068646')['title'] == text_type(u'The Godfather')
    True

    >>> Imdb('0133093')['title'] == text_type(u'The Matrix')
    True
    '''
    regex = {
        'alternativeTitles': {
            'page': 'releaseinfo',
            're': [
                '<table[^>]*?id="akas"[^>]*?>(.*?)</table>',
                "td>(.*?)</td>.*?<td>(.*?)</td>"
            ],
            'type': 'list'
        },
        'aspectratio': {
            'page': 'reference',
            're': [
                'Aspect Ratio</td>.*?ipl-inline-list__item">\s+([\d\.\:\ ]+)',
                parse_aspectratio,
            ],
            'type': 'float',
        },
        'budget': zebra_table('Budget', more=[
            lambda data: find_re(decode_html(data).replace(',', ''), '\d+')
        ], type='int'),
        'cast': {
            'page': 'reference',
            're': [
                ' <table class="cast_list">(.*?)</table>',
                '<td.*?itemprop="actor".*?>.*?>(.*?)</a>.*?<td class="character">(.*?)</td>',
                lambda ll: [strip_tags(l) for l in ll] if isinstance(ll, list) else strip_tags(ll)
            ],
            'type': 'list'
        },
        'cinematographer': reference_section('cinematographers'),
        'connections': {
            'page': 'movieconnections',
            're': '<h4 class="li_group">(.*?)</h4>(.*?)(<\/div>\n  <a|<script)',
            'type': 'list'
        },
        'country': zebra_list('Country', more=['<a.*?>(.*?)</a>']),
        'creator': {
            'page': '',
            're': [
                '<div class="credit_summary_item">.*?<h4.*?>Creator.?:</h4>(.*?)</div>',
                '<a href="/name/.*?>(.*?)</a>',
                lambda ll: strip_tags(ll)
            ],
            'type': 'list'
        },
        'director': reference_section('directors'),
        'editor': reference_section('editors'),
        'composer': reference_section('composers'),
        'episodeTitle': {
            'page': 'reference',
            're': '<h3 itemprop="name">(.*?)<',
            'type': 'string'
        },
        'filmingLocations': {
            'page': 'locations',
            're': [
                '<a href="/search/title\?locations=.*?".*?>(.*?)</a>',
                lambda data: data.strip(),
            ],
            'type': 'list'
        },
        'genre': zebra_list('Genres', more=['<a.*?>(.*?)</a>']),
        'gross': zebra_table('Cumulative Worldwide Gross', more=[
            lambda data: find_re(decode_html(data).replace(',', ''), '\d+')
        ], type='int'),
        'keyword': {
            'page': 'keywords',
            're': '<a href="/keyword/.*?>(.*?)</a>',
            'type': 'list'
        },
        'language': zebra_list('Language', more=['<a.*?>(.*?)</a>']),
        'originalTitle': {
            'page': 'releaseinfo',
            're': '<td>\(original title\)</td>\s*<td>(.*?)</td>',
            'type': 'string'
        },
        'summary': zebra_table('Plot Summary', more=[
            '<p>(.*?)<em'
        ]),
        'posterId': {
            'page': 'reference',
            're': '<img.*?class="titlereference-primary-image".*?src="(.*?)".*?>',
            'type': 'string'
        },
        'producer': reference_section('producers'),
        'productionCompany': {
            'page': 'reference',
            're': [
                'Production Companies.*?<ul(.*?)</ul>',
                '<a href="/company/.*?/">(.*?)</a>'
            ],
            'type': 'list'
        },
        'rating': {
            'page': 'reference',
            're': [
                '<div class="ipl-rating-star ">(.*?)</div>',
                'ipl-rating-star__rating">([\d,.]+?)</span>',
            ],
            'type': 'float'
        },
        'releasedate': {
            'page': 'releaseinfo',
            're': [
                '<td class="release_date">(.*?)</td>',
                strip_tags,
            ],
            'type': 'list'
        },
        #FIXME using some /offsite/ redirect now
        #'reviews': {
        #    'page': 'externalreviews',
        #    're': [
        #        '<ul class="simpleList">(.*?)</ul>',
        #        '<li>.*?<a href="(http.*?)".*?>(.*?)</a>.*?</li>'
        #    ],
        #    'type': 'list'
        #},
        'runtime': zebra_list('Runtime'),
        'color': zebra_list('Color', more=[
            '<a.*?>([^(<]+)',
            lambda r: r[0] if isinstance(r, list) else r,
            strip_tags
        ]),
        'sound': zebra_list('Sound Mix', more=[
            '<a.*?>([^(<]+)',
            lambda r: r[0] if isinstance(r, list) else r,
            strip_tags
        ]),
        'season': {
            'page': 'reference',
            're': [
                '<ul class="ipl-inline-list titlereference-overview-season-episode-numbers">(.*?)</ul>',
                'Season (\d+)',
             ],
            'type': 'int'
        },
        'episode': {
            'page': 'reference',
            're': [
                '<ul class="ipl-inline-list titlereference-overview-season-episode-numbers">(.*?)</ul>',
                'Episode (\d+)',
             ],
            'type': 'int'
        },
        'series': {
            'page': 'reference',
            're': '<h4 itemprop="name">.*?<a href="/title/tt(\d{7})',
            'type': 'string'
        },
        'isSeries': {
            'page': 'reference',
            're': 'property=\'og:title\'.*?content=".*?(TV series|TV mini-series).*?"',
            'type': 'string'
        },
        'title': {
            'page': 'releaseinfo',
            're': 'h3 itemprop="name">.*?>(.*?)</a>',
            'type': 'string'
        },
        'trivia': {
            'page': 'trivia',
            're': [
                '<div class="sodatext">(.*?)<(br|/div)',
                lambda data: data[0]
            ],
            'type': 'list',
        },
        'votes': {
            'page': 'reference',
            're': [
                'class="ipl-rating-star__total-votes">\((.*?)\)',
                lambda r: r.replace(',', '')
            ],
            'type': 'string'
        },
        'writer': reference_section('writers'),
        'year': {
            'page': 'reference',
            're': '<a href="/search/title\?year=\d+&ref_=tt_rv".*?itemprop=\'url\'>(\d+)</a>',
            'type': 'int'
        },
        'credits': {
            'page': 'fullcredits',
            're': [
                lambda data: data.split('<h4'),
                '>(.*?)</h4>.*?(<table.*?</table>)',
                lambda data: [d for d in data if d]
            ],
            'type': 'list'
        },
    }

    def read_url(self, url, timeout):
        if url not in self._cache:
            self._cache[url] = read_url(url, timeout=timeout, unicode=True)
        return self._cache[url]

    def __init__(self, id, timeout=-1):
        # use akas.imdb.com to always get original title:
        # http://www.imdb.com/help/show_leaf?titlelanguagedisplay
        self.baseUrl = "http://www.imdb.com/title/tt%s/" % id
        super(Imdb, self).__init__(timeout)

        url = self.baseUrl + 'reference'
        page = self.read_url(url, timeout=-1)
        if '<title>IMDb: Page not found</title>' in page \
            or 'The requested URL was not found on our server.' in page:
            return
        if "<p>We're sorry, something went wrong.</p>" in page:
            time.sleep(1)
            super(Imdb, self).__init__(0)

        if 'alternativeTitles' in self:
            if len(self['alternativeTitles']) == 2 and \
               isinstance(self['alternativeTitles'][0], string_types):
               self['alternativeTitles'] = [self['alternativeTitles']]

        for key in ('country', 'genre', 'language', 'sound', 'color'):
            if key in self:
                self[key] = [x[0] if len(x) == 1 and isinstance(x, list) else x for x in self[key]]
                self[key] = list(filter(lambda x: x.lower() != 'home', self[key]))

        #normalize country names
        if 'country' in self:
            self['country'] = [normalize_country_name(c) or c for c in self['country']]


        def cleanup_title(title):
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            if title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            title = re.sub('\(\#[.\d]+\)', '', title)
            return title.strip()

        for t in ('title', 'originalTitle'):
            if t in self:
                self[t] = cleanup_title(self[t])

        if 'alternativeTitles' in self:
            alt = {}
            for t in self['alternativeTitles']:
                title = cleanup_title(t[1])
                if title.lower() not in (self.get('title', '').lower(), self.get('originalTitle', '').lower()):
                    if title not in alt:
                        alt[title] = []
                    for c in t[0].split('/'):
                        for cleanup in ('International', '(working title)', 'World-wide'):
                            c = c.replace(cleanup, '')
                        c = c.split('(')[0].strip()
                        if c:
                            alt[title].append(c)
            self['alternativeTitles'] = []
            for t in sorted(alt, key=lambda a: sorted(alt[a])):
                countries = sorted(set([normalize_country_name(c) or c for c in alt[t]]))
                self['alternativeTitles'].append((t, countries))
            if not self['alternativeTitles']:
                del self['alternativeTitles']

        if 'runtime' in self and self['runtime']:
            if isinstance(self['runtime'], list):
                self['runtime'] = self['runtime'][0]
            if 'min' in self['runtime']:
                base = 60
            else:
                base = 1
            self['runtime'] = int(find_re(self['runtime'], '([0-9]+)')) * base
        if 'runtime' in self and not self['runtime']:
            del self['runtime']

        if 'sound' in self:
            self['sound'] = list(sorted(set(self['sound'])))

        if 'cast' in self:
            if isinstance(self['cast'][0], string_types):
                self['cast'] = [self['cast']]
            self['actor'] = [c[0] for c in self['cast']]
            def cleanup_character(c):
                c = c.replace('(uncredited)', '').strip()
                c = re.sub('\s+', ' ', c)
                return c
            self['cast'] = [{'actor': x[0], 'character': cleanup_character(x[1])}
                            for x in self['cast']]

        if 'connections' in self:
            cc={}
            if len(self['connections']) == 3 and isinstance(self['connections'][0], string_types):
                self['connections'] = [self['connections']]
            for rel, data, _ in self['connections']:
                if isinstance(rel, bytes):
                    rel = rel.decode('utf-8')
                #cc[rel] = re.compile('<a href="/title/tt(\d{7})/">(.*?)</a>').findall(data)
                def get_conn(c):
                    r = {
                        'id': c[0],
                        'title': cleanup_title(c[1]),
                    }
                    description = c[2].split('<br />')
                    if len(description) == 2 and description[-1].strip() != '-':
                        r['description'] = description[-1].strip()
                    return r
                cc[rel] = list(map(get_conn, re.compile('<a href="/title/tt(\d{7})/?">(.*?)</a>(.*?)<\/div', re.DOTALL).findall(data)))

            self['connections'] = cc

        if 'isSeries' in self:
            del self['isSeries']
            self['isSeries'] = True
        if 'episodeTitle' in self:
            self['episodeTitle'] = re.sub('Episode \#\d+\.\d+', '', self['episodeTitle'])

        if 'series' in self:
            series = Imdb(self['series'], timeout=timeout)
            self['seriesTitle'] = series['title']
            if 'episodeTitle' in self:
                self['seriesTitle'] = series['title']
                if 'season' in self and 'episode' in self:
                    self['title'] = "%s (S%02dE%02d) %s" % (
                        self['seriesTitle'], self['season'], self['episode'], self['episodeTitle'])
                else:
                    self['title'] = "%s (S01) %s" % (self['seriesTitle'], self['episodeTitle'])
                    self['season'] = 1
                self['title'] = self['title'].strip()
            if 'director' in self:
                self['episodeDirector'] = self['director']

            if 'creator' not in series and 'director' in series:
                series['creator'] = series['director']
                if len(series['creator']) > 10:
                    series['creator'] = series['director'][:1]

            for key in ['creator', 'country']:
                if key in series:
                    self[key] = series[key]

            if 'year' in series:
                self['seriesYear'] = series['year']
                if not 'year' in self:
                    self['year'] = series['year']

            if 'year' in self:
                self['episodeYear'] = self['year']
            if 'creator' in self:
                self['seriesDirector'] = self['creator']
            if 'originalTitle' in self:
                del self['originalTitle']
        else:
            for key in ('seriesTitle', 'episodeTitle', 'season', 'episode'):
                if key in self:
                    del self[key]
        if 'creator' in self:
            if 'director' in self:
                self['episodeDirector'] = self['director']
            self['director'] = self['creator']

        #make lists unique but keep order
        for key in ('director', 'language'):
            if key in self:
                self[key] = [x for i,x in enumerate(self[key])
                             if x not in self[key][i+1:]]

        for key in ('actor', 'writer', 'producer', 'editor', 'composer'):
            if key in self:
                if isinstance(self[key][0], list):
                    self[key] = [i[0] for i in self[key] if i]
                self[key] = sorted(list(set(self[key])), key=lambda a: self[key].index(a))


        if 'budget' in self and 'gross' in self:
            self['profit'] = self['gross'] - self['budget']

        if 'releasedate' in self:
            def parse_date(d):
                try:
                    d = datetime.strptime(d, '%d %B %Y')
                except:
                    try:
                        d = datetime.strptime(d, '%B %Y')
                    except:
                        return 'x'
                return '%d-%02d-%02d' % (d.year, d.month, d.day)
            self['releasedate'] = min([
                parse_date(d) for d in self['releasedate']
            ])
            if self['releasedate'] == 'x':
                del self['releasedate']
        if 'summary' in self:
            if isinstance(self['summary'], list):
                self['summary'] = self['summary'][0]
            self['summary'] = self['summary'].split('</p')[0].strip()

        if 'credits' in self:
            credits = [
                [
                    strip_tags(d[0].replace(' by', '')).strip(),
                    [
                        [
                            strip_tags(x[0]).strip(),
                            [t.strip().split(' (')[0].strip() for t in x[2].split(' / ')]
                        ]
                        for x in
                        re.compile('<td class="name">(.*?)</td>.*?<td>(.*?)</td>.*?<td class="credit">(.*?)</td>', re.DOTALL).findall(d[1])
                    ]
                ] for d in self['credits'] if d
            ]
            credits = [c for c in credits if c[1]]

            self['credits'] = []
            for department, crew in credits:
                department = department.replace('(in alphabetical order)', '').strip()
                for c in crew:
                    self['credits'].append({
                        'name': c[0],
                        'roles': c[1],
                        'deparment': department
                    })
            if not self['credits']:
                del self['credits']

class ImdbCombined(Imdb):
    def __init__(self, id, timeout=-1):
        _regex = {}
        for key in self.regex:
            if self.regex[key]['page'] in ('releaseinfo', 'reference'):
                _regex[key] = self.regex[key]
        self.regex = _regex
        super(ImdbCombined, self).__init__(id, timeout)

def get_movie_by_title(title, timeout=-1):
    '''
    This only works for exact title matches from the data dump
    Usually in the format
        Title (Year)
        "Series Title" (Year) {(#Season.Episode)}
        "Series Title" (Year) {Episode Title (#Season.Episode)}

    If there is more than one film with that title for the year
        Title (Year/I)

    >>> str(get_movie_by_title(u'"Father Knows Best" (1954) {(#5.34)}'))
    '1602860'

    >>> str(get_movie_by_title(u'The Matrix (1999)'))
    '0133093'

    >>> str(get_movie_by_title(u'Little Egypt (1951)'))
    '0043748'

    >>> str(get_movie_by_title(u'Little Egypt (1897/I)'))
    '0214882'

    >>> get_movie_by_title(u'Little Egypt')
    None 

    >>> str(get_movie_by_title(u'"Dexter" (2006) {Father Knows Best (#1.9)}'))
    '0866567'
    '''
    params = {'s': 'tt', 'q': title}
    if not isinstance(title, bytes):
        try:
            params['q'] = unicodedata.normalize('NFKC', params['q']).encode('latin-1')
        except:
            params['q'] = params['q'].encode('utf-8')
    params = urlencode(params)
    url = "http://akas.imdb.com/find?" + params
    data = read_url(url, timeout=timeout, unicode=True)
    #if search results in redirect, get id of current page
    r = '<meta property="og:url" content="http://www.imdb.com/title/tt(\d{7})/" />'
    results = re.compile(r).findall(data)    
    if results:
        return results[0]
    return None
 
def get_movie_id(title, director='', year='', timeout=-1):
    '''
    >>> str(get_movie_id('The Matrix'))
    '0133093'

    >>> str(get_movie_id('2 or 3 Things I Know About Her', 'Jean-Luc Godard'))
    '0060304'

    >>> str(get_movie_id('2 or 3 Things I Know About Her', 'Jean-Luc Godard', '1967'))
    '0060304'

    >>> str(get_movie_id(u"Histoire(s) du cinema: Le controle de l'univers", u'Jean-Luc Godard'))
    '0179214'

    >>> str(get_movie_id(u"Histoire(s) du cinéma: Le contrôle de l'univers", u'Jean-Luc Godard'))
    '0179214'

    '''
    imdbId = {
        (u'Le jour se l\xe8ve', u'Marcel Carn\xe9'): '0031514',
        (u'Wings', u'Larisa Shepitko'): '0061196',
        (u'The Ascent', u'Larisa Shepitko'): '0075404',
        (u'Fanny and Alexander', u'Ingmar Bergman'): '0083922',
        (u'Torment', u'Alf Sj\xf6berg'): '0036914',
        (u'Crisis', u'Ingmar Bergman'): '0038675',
        (u'To Joy', u'Ingmar Bergman'): '0043048',
        (u'Humain, trop humain', u'Louis Malle'): '0071635',
        (u'Place de la R\xe9publique', u'Louis Malle'): '0071999',
        (u'God\u2019s Country', u'Louis Malle'): '0091125',
        (u'Flunky, Work Hard', u'Mikio Naruse'): '0022036',
        (u'The Courtesans of Bombay', u'Richard Robbins') : '0163591',
        (u'Je tu il elle', u'Chantal Akerman') : '0071690',
        (u'Hotel Monterey', u'Chantal Akerman') : '0068725',
        (u'No Blood Relation', u'Mikio Naruse') : '023261',
        (u'Apart from You', u'Mikio Naruse') : '0024214',
        (u'Every-Night Dreams', u'Mikio Naruse') : '0024793',
        (u'Street Without End', u'Mikio Naruse') : '0025338',
        (u'Sisters of the Gion', u'Kenji Mizoguchi') : '0027672',
        (u'Osaka Elegy', u'Kenji Mizoguchi') : '0028021',
        (u'Blaise Pascal', u'Roberto Rossellini') : '0066839',
        (u'Japanese Girls at the Harbor', u'Hiroshi Shimizu') : '0160535',
        (u'The Private Life of Don Juan', u'Alexander Korda') : '0025681',
        (u'Last Holiday', u'Henry Cass') : '0042665',
        (u'A Colt Is My Passport', u'Takashi  Nomura') : '0330536',
        (u'Androcles and the Lion', u'Chester Erskine') : '0044355',
        (u'Major Barbara', u'Gabriel Pascal') : '0033868',
        (u'Come On Children', u'Allan King') : '0269104',

        (u'Jimi Plays Monterey & Shake! Otis at Monterey', u'D. A. Pennebaker and Chris Hegedus') : '',
        (u'Martha Graham: Dance on Film', u'Nathan Kroll') : '',
        (u'Carmen', u'Carlos Saura'): '0085297',
        (u'The Story of a Cheat', u'Sacha Guitry'): '0028201',
        (u'Weekend', 'Andrew Haigh'): '1714210',
    }.get((title, director), None)
    if imdbId:
        return imdbId
    params = {'s': 'tt', 'q': title}
    if director:
        params['q'] = u'"%s" %s' % (title, director)
    if year:
        params['q'] = u'"%s (%s)" %s' % (title, year, director)
    google_query = "site:imdb.com %s" % params['q']
    if not isinstance(params['q'], bytes):
        try:
            params['q'] = unicodedata.normalize('NFKC', params['q']).encode('latin-1')
        except:
            params['q'] = params['q'].encode('utf-8')
    params = urlencode(params)
    url = "http://akas.imdb.com/find?" + params
    #print url

    data = read_url(url, timeout=timeout, unicode=True)
    #if search results in redirect, get id of current page
    r = '<meta property="og:url" content="http://www.imdb.com/title/tt(\d{7})/" />'
    results = re.compile(r).findall(data)    
    if results:
        return results[0]
    #otherwise get first result
    r = '<td valign="top">.*?<a href="/title/tt(\d{7})/"'
    results = re.compile(r).findall(data)
    if results:
        return results[0]

    #print((title, director), ": '',")
    #print(google_query)
    #results = google.find(google_query, timeout=timeout)
    results = duckduckgo.find(google_query, timeout=timeout)
    if results:
        for r in results[:2]:
            imdbId = find_re(r[1], 'title/tt(\d{7})')
            if imdbId:
                return imdbId
    #or nothing
    return ''

def get_movie_poster(imdbId):
    '''
    >>> get_movie_poster('0133093')
    'http://ia.media-imdb.com/images/M/MV5BMjEzNjg1NTg2NV5BMl5BanBnXkFtZTYwNjY3MzQ5._V1._SX338_SY475_.jpg'
    '''
    info = ImdbCombined(imdbId)
    if 'posterId' in info:
        poster = info['posterId']
        if '@._V' in poster:
            poster = poster.split('@._V')[0] + '@.jpg'
        return poster
    elif 'series' in info:
        return get_movie_poster(info['series'])
    return ''

def get_episodes(imdbId, season=None):
    episodes = {}
    url = 'http://www.imdb.com/title/tt%s/episodes' % imdbId
    if season:
        url += '?season=%d' % season
        data = cache.read_url(url)
        for e in re.compile('<div data-const="tt(\d{7})".*?>.*?<div>S(\d+), Ep(\d+)<\/div>\n<\/div>', re.DOTALL).findall(data):
            episodes['S%02dE%02d' % (int(e[1]), int(e[2]))] = e[0]
    else:
        data = cache.read_url(url)
        match = re.compile('<strong>Season (\d+)</strong>').findall(data)
        if match:
            for season in range(1, int(match[0]) + 1):
               episodes.update(get_episodes(imdbId, season))
    return episodes

def max_votes():
    url = 'http://www.imdb.com/search/title?num_votes=500000,&sort=num_votes,desc'
    data = cache.read_url(url).decode('utf-8', 'ignore')
    votes = max([
        int(v.replace(',', ''))
        for v in re.compile('<span name="nv" data-value="(\d+)"').findall(data)
    ])
    return votes

def guess(title, director='', timeout=-1):
    return get_movie_id(title, director, timeout=timeout)

if __name__ == "__main__":
    import json
    print(json.dumps(Imdb('0306414'), indent=2))
    #print json.dumps(Imdb('0133093'), indent=2)

