from .xpath import XPath


class Alioth(XPath):
    name = 'alioth'

    def parse(self, response):
        meta = response.meta
        meta.update(XPath.params)
        meta['base'] = ('//table[@summary=\'Latest file releases\']//tr/td[1]'
                        '[re:test(., \'\\b{}\\b\')]'.format(
                            meta.get('package', meta['id'])))
        meta['date'] = '/following-sibling::td/following-sibling::td'
        meta['version'] = '/following-sibling::td'
        return super().parse(response)

    def first_request(self, data):
        return "https://alioth.debian.org/projects/{}/".format(
                data.get('project', data['id']))
