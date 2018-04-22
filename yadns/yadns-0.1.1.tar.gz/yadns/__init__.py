from requests import Request, Session


class YaDNS:
    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.api_url = 'https://pddimp.yandex.ru/api2/admin/dns/{}'
        self.session = Session()
        self.headers = {
            'Host': 'pddimp.yandex.ru',
            'PddToken': token,
        }

    def add(
        self, r_type, content, subdomain, ttl=None, mail=None, prio=None,
        weight=None, port=None, target=None,
    ):
        params = {
            'domain': self.domain,
            'type': r_type,
            'admin_mail': mail,
            'content': content,
            'priority': prio,
            'weight': weight,
            'port': port,
            'target': target,
            'subdomain': subdomain,
            'ttl': ttl,
        }

        data = {}
        for k, v in params.iteritems():
            if v is not None:
                data.update({k: v})

        req = Request(
            'POST',
            url=self.api_url.format('add'),
            headers=self.headers,
            data=data,
        )
        prepped = req.prepare()
        resp = self.session.send(prepped)

        return resp.json()

    def list(self):
        data = {'domain': self.domain}
        req = Request(
            'GET',
            url=self.api_url.format('list'),
            headers=self.headers,
            data=data,
        )
        prepped = req.prepare()
        resp = self.session.send(prepped)

        return resp.json()

    def edit(
        self, record_id, mail=None, content=None, prio=None, weight=None,
        port=None, target=None, subdomain=None, ttl=None, refresh=None,
        retry=None, expire=None, neg_cache=None,
    ):
        zone = self.list()

        data = {}
        for r in zone['records']:
            if str(r['record_id']) == record_id:
                data = r
                break
        data.pop('fqdn')

        params = {
            'domain': self.domain,
            'record_id': record_id,
            'admin_mail': mail,
            'content': content,
            'priority': prio,
            'weight': weight,
            'port': port,
            'target': target,
            'subdomain': subdomain,
            'ttl': ttl,
            'refresh': refresh,
            'retry': retry,
            'expire': expire,
            'neg_cache': neg_cache,
        }

        for k, v in params.iteritems():
            if v is not None:
                data.update({k: v})

        req = Request(
            'POST',
            url=self.api_url.format('edit'),
            headers=self.headers,
            data=data,
        )

        prepped = req.prepare()
        resp = self.session.send(prepped)

        return resp.json()

    def delete(self, record_id):
        data = {
            'domain': self.domain,
            'record_id': record_id,
        }
        req = Request(
            'POST',
            url=self.api_url.format('del'),
            headers=self.headers,
            data=data,
        )
        prepped = req.prepare()
        resp = self.session.send(prepped)

        return resp.json()
