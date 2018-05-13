import re
from multiprocessing import Pool

import pandas
import requests

from tba_pydata import constants

TBA = 'https://www.thebluealliance.com/api/v3'
HEADER = {'X-TBA-Auth_Key': ''}
YEAR = 2018

TEAM_REGEX = re.compile(r'frc([0-9]+).*')


def config(key=None, endpoint='https://www.thebluealliance.com/api/v3', year=2018, **kwargs):
    global HEADER
    HEADER['X-TBA-Auth_Key'] = key
    global TBA
    TBA = endpoint
    global YEAR
    YEAR = year

    print(str(HEADER))


# ------------------------


def tba_fetch(path):
    resp = requests.get(TBA + path, headers=HEADER)
    print(TBA + path, resp.status_code)
    return resp.json()


def tba_fetch_many(paths, concat=True):
    pool = Pool()
    res = pool.map(tba_fetch, paths)

    if not concat:
        return res

    total = []
    for sublist in res:
        total += sublist

    return total


def normalize_team_key(team, out_format='tba'):
    if isinstance(team, int):
        if out_format == 'int':
            return team
        elif out_format == 'str':
            return 'frc%04d' % team
        elif out_format == 'tba':
            return 'frc%d' % team
        else:
            return None
    elif isinstance(team, str):
        matches = TEAM_REGEX.match(team)
        if matches:
            num = matches.group(1)
            if out_format == 'str':
                return 'frc%04d' % int(num)
            elif out_format == 'int':
                return int(num)
            elif out_format == 'tba':
                return 'frc%d' % int(num)
        else:
            return normalize_team_key(int(team), out_format)


def opp(alliance):
    alliance = alliance.lower()
    return 'blue' if alliance == 'red' else 'red'


# ------------------------


def status():
    res = tba_fetch('/status')
    return pandas.Series(res)


def teams(page=-1, year=None, form=None, district=None):
    url = ("/district/%s/teams/" % district) if district is not None else '/teams/'

    if page != -1:
        if year is None:
            if form is None:
                res = tba_fetch(url + str(page))
            else:
                res = tba_fetch(url + '%d/%s' % (page, form))
        else:
            if form is None:
                res = tba_fetch(url + '%d/%d' % (year, page))
            else:
                res = tba_fetch(url + '%d/%d/%s' % (year, page, form))

        if len(res) == 0:
            return None
        else:
            if form == 'keys':
                return pandas.Series(res)
            else:
                data = pandas.DataFrame(res)
    else:
        pages = range(15)
        if year is None:
            if form is None:
                paths = (url + str(page) for page in pages)
            else:
                paths = (url + '%d/%s' % (page, form) for page in pages)
        else:
            if form is None:
                paths = (url + '%d/%d' % (year, page) for page in pages)
            else:
                paths = (url + '%d/%d/%s' % (year, page, form) for page in pages)

        res = tba_fetch_many(paths)
        if form == 'keys':
            return pandas.Series(res)
        else:
            data = pandas.DataFrame(res)

    champs_year = '2018' if (year is None or year < 2017) else str(year)
    data['home_championship'] = data.home_championship.apply(lambda val: val[champs_year] if val is not None else None)
    data['state_prov'] = data.state_prov.apply(lambda loc: constants.STATE_PROV_NORMALIZATION[loc])
    data.index = data['team_number']

    return data


def events(team=None, year=None, form=None, district=None):
    if team is not None:
        team = normalize_team_key(team)
        url = "/team/%s/events" % team
        if year is not None:
            url += "/" + str(year)

        if form is not None:
            url += "/" + form

        res = tba_fetch(url)
        if form == 'keys':
            return pandas.Series(res)
        else:
            data = pandas.DataFrame(res)
    else:
        if district is not None:
            url = "/district/%s/" % district
        else:
            url = "/"

        url += "events"
        if year is not None:
            url += "/" + str(year)

        if form is not None:
            url += "/" + form

        res = tba_fetch(url)
        if form == 'keys':
            return pandas.Series(res)
        else:
            data = pandas.DataFrame(res)

    data['district'] = data.district.apply(lambda val: val['abbreviation'] if val is not None else None)
    data.index = data['key']
    return data


def matches(team=None, event=None, year=YEAR, form=None, score_parsing_fn=None, event_predicate=None, district=None):
    year = year if district is None else None
    if team is not None:
        team = normalize_team_key(team)
        url_bits = ['team', team]

        if event is not None:
            url_bits.append('event')
            url_bits.append(event)

        url_bits.append('matches')
        if event is None:
            url_bits.append(str(year))
        if form is not None:
            url_bits.append(form)

        url = '/' + '/'.join(url_bits)
        res = tba_fetch(url)

        if form == 'keys':
            return pandas.Series(res)

        data = []
        for entry in res:
            row = entry
            alliances = entry['alliances']
            alliance = 'red' if team in alliances['red']['team_keys'] else 'blue'
            row['alliance'] = alliance

            i = 1
            for team_key in alliances[alliance]['team_keys']:
                row[alliance + str(i)] = team_key
                if team_key == team:
                    row['position'] = alliance + str(i)
                i += 1

            i = 1
            for team_key in alliances[opp(alliance)]['team_keys']:
                row[opp(alliance) + str(i)] = team_key
                i += 1

            if team in alliances[alliance]['surrogate_team_keys']:
                row['was_surrogate'] = True

            row['score'] = alliances[alliance]['score']
            row['opp_score'] = alliances[opp(alliance)]['score']

            if form is None and score_parsing_fn is not None:
                if row['score'] != -1:
                    data.append(score_parsing_fn(row))
                else:
                    pass
            else:
                data.append(row)

        df = pandas.DataFrame(data)
        df.index = df['key']
        return df

    elif event is not None:
        url_bits = ['event', event, 'matches']
        if form is not None:
            url_bits.append(form)

        url = '/' + '/'.join(url_bits)
        res = tba_fetch(url)

    else:
        assert (year is not None or district is not None)
        if event_predicate is None:
            event_keys = events(team=team, year=year, district=district, form='keys')
        else:
            evs = events(team=team, year=year, district=district)
            event_keys = evs[event_predicate(evs)].index

        if form is None:
            path_gen = ("/event/%s/matches" % v for v in event_keys)
        else:
            path_gen = ("/event/%s/matches/%s" % (v, form) for v in event_keys)

        res = tba_fetch_many(path_gen)

    if form == 'keys':
        return pandas.Series(res)

    data = []
    for entry in res:
        row = entry
        alliances = entry['alliances']

        i = 1
        for team_key in alliances['blue']['team_keys']:
            row['blue' + str(i)] = team_key
            i += 1

        i = 1
        for team_key in alliances['red']['team_keys']:
            row['red' + str(i)] = team_key
            i += 1

        row['red_score'] = alliances['red']['score']
        row['blue_score'] = alliances['blue']['score']

        if form is None and score_parsing_fn is not None:
            if row['red_score'] != -1:
                data.append(score_parsing_fn(row))
            else:
                pass
        else:
            data.append(row)

    df = pandas.DataFrame(data)
    df.index = df['key']
    return df


def event_finish(event):
    ranks = tba_fetch('/event/%s/rankings' % event)
    alliances = tba_fetch('/event/%s/alliances' % event)

    table = {}
    for rank in ranks['rankings']:
        record = {
            'rank': rank['rank'],
            'wins': rank['record']['wins'],
            'ties': rank['record']['ties'],
            'losses': rank['record']['losses'],
            'pick': -1,
            'seed': -1,
            'finish': 'np'
        }

        for i, cat in enumerate(ranks['sort_order_info']):
            record[cat['name']] = rank['sort_orders'][i]

        table[rank['team_key']] = record

    for i, alliance in enumerate(alliances):
        if alliance['status']['status'] == 'won':
            finish = 'won'
        else:
            finish = alliance['status']['level']

        for role, team in enumerate(alliance['picks']):
            table[team]['pick'] = role
            table[team]['seed'] = i+1
            table[team]['finish'] = finish

    return pandas.DataFrame.from_dict(table, orient='index')
