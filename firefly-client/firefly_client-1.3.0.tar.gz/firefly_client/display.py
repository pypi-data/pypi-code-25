
"""
`firefly_client.display` is a state-base interface to firefly_client,
inspired by `matplotlib.pyplot`.
"""

import logging
import os
import sys
import urllib
from astropy.io import fits
from ws4py.client import HandshakeError
from .firefly_client import FireflyClient

logger = logging.getLogger(__name__)

public_hosts = ['https://lsst-demo.ncsa.illinois.edu']

try_urls = []

if 'FIREFLY_URL' in os.environ:
    try_urls.append(os.environ['FIREFLY_URL'])
if 'EXTERNAL_URL' in os.environ:
    try_urls.append(os.environ['EXTERNAL_URL'])
if 'FIREFLY_ROUTE' in os.environ:
    basedir = os.environ['FIREFLY_ROUTE']
else:
    basedir = 'firefly'

try_urls.append('http://localhost:8080')
try_urls.append('http://127.0.0.1:8080')

try_urls += public_hosts

for url in try_urls:
    try:
        _ = urllib.parse.urlparse(url)
        host_url = _.scheme + '://' + _.netloc
        logger.debug('attempting to connect to {}'.format(host_url))
        fc = FireflyClient(host_url, basedir=basedir, html_file='slate.html')
        break
    except Exception:
        logger.debug('connection failed to {}'.format(host_url))

fc.launch_browser()

frame_ctr = None

def imshow(data, vmin=None, vmax=None, cmap=1, title=None):
    """display an array or astropy.io.fits HDU or HDUList

    Parameters:
    -----------
    data: 2-D numpy array, or FITS object with write method
        Data to show in Firefly
    vmin, vmax: `float` or `str`
        minimum or maximum values, or a value like 'zscale' or 'minmax'
    cmap: `str`
        name of colormap
    title: `str`
        title for the plot, if None then an integer is used

    """
    return




