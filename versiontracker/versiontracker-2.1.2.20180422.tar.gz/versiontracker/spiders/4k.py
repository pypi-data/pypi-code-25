from .xpath import XPath


class FourK(XPath):
    name = '4k'

    def parse(self, response):
        meta = response.meta
        meta.update(XPath.params)
        meta['base'] = '//a[re:test(@href, \'/app/{}_\')]/parent::td/' \
                        'parent::tr/td'.format(meta['id'])
        meta['version'] = '[contains(@class, \'--version\')]'
        meta['date'] = '[contains(@class, \'--date\')]'
        return super().parse(response)

    def first_request(self, data):
        return 'https://www.4kdownload.com/download'
