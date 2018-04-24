import os, logging

import time

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
import requests

log = logging.getLogger('allgo')
__version__ = '0.1.1'

def _in_ipynb():
    try:
        cfg = get_ipython().config
        if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
            return True
        else:
            return False
    except NameError:
        return False


def _token():
    if _in_ipynb():
        from IPython.display import display, HTML
        js = "<script>  IPython.notebook.kernel.execute(\"cookie = '\" + document.cookie + \"'\");</script>"
        display(HTML(js))
        cookie = {k: v for k, v in [c.split('=') for c in cookie.replace(' ', '').split(';')]}
        if 'atk' in cookie.keys():
            return cookie['atk']
    elif 'ALLGO_TOKEN' in os.environ.keys():
        return os.get['ALLGO_TOKEN']
    else:
        return None


token = _token()


class App:
    """
    AllGo app submission object
    """

    def __init__(self, name, token=None):
        """
        Constructor
        :param name: name of the application in lower case
        :param token: if not provided, we check ALLGO_TOKEN env variable and notebook parameters
        """
        self.name = name
        self.token = token if token else token()

    def run(self, files, outputdir='.', params=''):
        """
        Submit the job
        :param files: input files
        :param outputdir: by default current directory
        :param params: a string parameters see the application documentation
        :return:
        """
        headers = {'Authorization': 'Token token={}'.format(_token)}
        data = {"job[webapp_name]": self.name,
                "job[param]": params}
        ALLGO_URL = os.environ.get('ALLGO_URL', "https://allgo.inria.fr")
        r = requests.post('%s/api/v1/jobs' % ALLGO_URL, headers=headers, files=files, data=data)
        r.raise_for_status()
        jobid = r['id']
        results = None
        while True:
            r = requests.get('{}/api/v1/jobs/{}'.format(ALLGO_URL, jobid), headers=headers)
            r.raise_for_status()
            results = r.json()
            status = results['status']
            if status == 'in progress':  # 'in progress', 'done', 'error', 'timeout'
                log.info("wait for job %s", jobid)
                time.sleep(2)
            else:
                break
        if status != 'done':
            raise Exception('Job %s failed with status %s', (jobid, status))

        elif status == 'done' and results:
            for filename, url in results[jobid].items:
                filepath = os.path.join(outputdir, filename)
                with open(filepath, 'wb') as fb:
                    fb.write(requests.get(url, stream=True).content)
