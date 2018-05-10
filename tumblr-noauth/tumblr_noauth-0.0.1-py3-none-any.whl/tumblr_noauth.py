from urllib.parse import urljoin, urlparse

# 3rd party
import requests
from beautifulsoup4 import BeautifulSoup

class TumblrSession(requests.Session):
    _prefix = 'https://www.tumblr.com/'

    def __init__(self, email, password):
        """
        email and password are used to login
        """
        self.usable = False
        login = self._login(email, password)
        if login.ok:
            self.usable = True
        else:
            raise ValueError(f'login failure; {login.status_code}')

    def __enter__(self):
        if not self.usable:
            raise ValueError(f'login failure; {login.status_code}')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.get('https://www.tumblr.com/logout')
        self.close()
        self.usable = False

    def __str__(self):
        return f'TumblrSession(usable={self.usable})'

    def __repr__(self):
        return str(self)

    # requests overrides

    def delete(self, url, **kwargs):
        return super().delete(self._resolve(url), **kwargs)

    def get(self, url, **kwargs):
        return super().get(self._resolve(url), **kwargs)

    def head(self, url, **kwargs):
        return super().head(self._resolve(url), **kwargs)

    def options(self, url, **kwargs):
        return super().options(self._resolve(url), **kwargs)

    def patch(self, url, **kwargs):
        return super().patch(self._resolve(url), **kwargs)

    def post(self, url, **kwargs):
        return super().post(self._resolve(url), **kwargs)

    def put(self, url, **kwargs):
        return super().put(self._resolve(url), **kwargs)

    # end requests overrides

    def _make_payload(self, form):
        """
        extract form <input>s to a dict
        form: a BS4 element or an object with .find_all and .attrs
        """
        payload = {}
        for inp in form.find_all('input'):
            if 'name' in inp.attrs:
                if 'value' in inp.attrs:
                    val = inp.attrs['value']
                else:
                    val = ''
                payload[inp.attrs['name']] = val
        return payload

    def _post_form(self, url, form=None, payload=None) -> requests.models.Response:
        """
        gets a form `form` from the page at `url` and posts its default values
        along with the data in `payload` to the form's destination; this is
        useful for capturing stuff like csrf tokens

        form: a beautifulSoup dict for selecting the form
        e.x. {'id': 'signup_form'}
        payload: extra data to send
        """
        if form == None:
            form = {}
        if payload == None:
            payload = {}

        pg = self.get(url)
        if not pg.ok:
            return pg

        form = BeautifulSoup(pg.text, 'html.parser').find(**form)
        if form == None:
            raise ValueError('No form found on page')

        final_payload = self._make_payload(form)
        final_payload.update(payload)
        del payload

        act = form['action']
        if (not act.startswith('http://') and not act.startswith('https://')):
            # relative url
            act = urljoin(pg.url, act)
        return self.post(act, data=final_payload)

    def _login(self, email, password):
        return self._post_form('https://www.tumblr.com/login',
            form={'id': 'signup_form'},
            payload={
                'determine_email': email,
                'user[email]':     email,
                'user[password]':  password,
            },
        )

    def _resolve(self, url):
        """
        resolves a possibl-relative-to-tumblr.com to an absolute url
        """
        if _is_absolute(url):
            return url
        else:
            return urljoin(self.prefix, act)

    # https://stackoverflow.com/a/8357518/5719760
    def _is_absolute(self, url):
        """
        true if url is absolute, false otherwise
        """
        return bool(urlparse(url).netloc)
