from .xpath import XPath


class PyPI(XPath):
    name = 'pypi'

    def parse(self, response):
        meta = response.meta
        meta.update(XPath.params)
        meta['base'] = '//div[contains(@class, \'release--current\')]'
        meta['version'] = \
            '//p[contains(@class, \'release__version\')]/a/text()'
        meta['date'] = '//time/@datetime'
        meta['url-xpath'] = \
            '//p[contains(@class, \'release__version\')]/a/@href'
        return super().parse(response)

    def first_request(self, data):
        data['package'] = data.get('package', data['id'])
        return "https://pypi.org/pypi/{}/".format(data['package'])
