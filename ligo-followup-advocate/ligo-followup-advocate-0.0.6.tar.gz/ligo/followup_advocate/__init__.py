from __future__ import print_function
import os
import shutil
import tempfile
from six.moves import urllib
import webbrowser

import astropy.time
from ligo.gracedb import rest
import lxml.etree

from .jinja import env
from .version import __version__  # noqa


def authors(authors, service=rest.DEFAULT_SERVICE_URL):
    """Write GCN Circular author list"""
    print(env.get_template('authors.txt').render(authors=authors).strip())


def guess_skyloc_pipeline(comments):
    comments = comments.upper()
    skyloc_pipelines = ['cWB', 'BAYESTAR', 'LIB', 'LALInference', 'UNKNOWN']
    for skyloc_pipeline in skyloc_pipelines:
        if skyloc_pipeline.upper() in comments:
            break
    return skyloc_pipeline


def compose(gracedb_id, authors=(), mailto=False,
            service=rest.DEFAULT_SERVICE_URL):
    """Compose GCN Circular draft"""
    client = rest.GraceDb(service)
    event = client.event(gracedb_id).json()
    voevents = client.voevents(gracedb_id).json()['voevents']
    log = client.logs(gracedb_id).json()['log']
    files = client.files(gracedb_id).json()

    gpstime = float(event['gpstime'])
    event_time = astropy.time.Time(gpstime, format='gps').utc

    skymaps = []
    for voevent in voevents:
        root = lxml.etree.fromstring(voevent['text'].encode('utf8'))
        alert_type = root.find(
            './What/Param[@name="AlertType"]').attrib['value'].lower()
        url = root.find('./What/Group/Param[@name="skymap_fits_basic"]')
        if url is None:
            continue
        url = url.attrib['value']
        _, filename = os.path.split(url)
        comments = '\n'.join(entry['comment'].upper() for entry in log
                             if entry['filename'] == filename)
        skyloc_pipeline = guess_skyloc_pipeline(comments)
        issued_time = astropy.time.Time(root.find('./Who/Date').text).datetime
        skymaps.append(dict(
            alert_type=alert_type,
            pipeline=skyloc_pipeline,
            filename=filename,
            latency=issued_time-event_time.datetime))

    em_brightfile = 'Source_Classification_{0}.json'.format(gracedb_id)
    if em_brightfile in files:
        source_classification = client.files(
            gracedb_id, em_brightfile).json()
    else:
        source_classification = {}

    kwargs = dict(
        gracedb_id=gracedb_id,
        group=event['group'],
        pipeline=event['pipeline'],
        gpstime='{0:.03f}'.format(round(float(event['gpstime']), 3)),
        search=event.get('search', ''),
        far=event['far'],
        utctime=event_time.iso,
        authors=authors,
        instruments=event['instruments'].split(','),
        skymaps=skymaps,
        prob_has_ns=source_classification.get('Prob NS2'),
        prob_has_remnant=source_classification.get('Prob EMbright'))

    subject = env.get_template('subject.txt').render(**kwargs).strip()
    body = env.get_template('circular.txt').render(**kwargs).strip()

    if mailto:
        pattern = 'mailto:emfollow@ligo.org,dac@ligo.org?subject={0}&body={1}'
        url = pattern.format(
            urllib.parse.quote(subject),
            urllib.parse.quote(body))
        webbrowser.open(url)
    else:
        string = '{0}\n{1}'.format(subject, body)
        print(string)
        return string


def read_map_gracedb(path, service=rest.DEFAULT_SERVICE_URL):
    import healpy as hp
    client = rest.GraceDb(service)
    with tempfile.NamedTemporaryFile() as localfile:
        remotefile = client.files(*path.split('/'), raw=True)
        try:
            shutil.copyfileobj(remotefile, localfile)
        finally:
            remotefile.close()
        localfile.flush()
        m = hp.read_map(localfile.name, verbose=False)
    return m


def mask_cl(p, level=90):
    import numpy as np
    pflat = p.ravel()
    i = np.flipud(np.argsort(p))
    cs = np.cumsum(pflat[i])
    cls = np.empty_like(pflat)
    cls[i] = cs
    cls = cls.reshape(p.shape)
    return cls <= 1e-2 * level


def compare_skymaps(paths, service=rest.DEFAULT_SERVICE_URL):
    """Produce table of sky map overlaps"""
    import healpy as hp
    filenames = [path.split('/')[1] for path in paths]
    pipelines = [guess_skyloc_pipeline(filename) for filename in filenames]
    probs = [read_map_gracedb(path, service) for path in paths]
    npix = max(len(prob) for prob in probs)
    nside = hp.npix2nside(npix)
    deg2perpix = hp.nside2pixarea(nside, degrees=True)
    probs = [hp.ud_grade(prob, nside, power=-2) for prob in probs]
    masks = [mask_cl(prob) for prob in probs]
    areas = [mask.sum() * deg2perpix for mask in masks]
    joint_areas = [(mask & masks[-1]).sum() * deg2perpix for mask in masks]

    kwargs = dict(params=zip(filenames, pipelines, areas, joint_areas))

    table = env.get_template('compare_skymaps.txt').render(**kwargs)
    print(table)
