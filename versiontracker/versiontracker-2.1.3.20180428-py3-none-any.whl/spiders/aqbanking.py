from .xpath import XPath


class AQBanking(XPath):
    name = 'aqbanking'

    def parse(self, response):
        meta = response.meta
        meta.update(XPath.params)
        meta['base'] = (
            '//body/table[3]//tr[1]/td[3]/table[2]/tr[position() mod 2 = 1 '
            'and position() > 3]/td[2]//a[1][not(re:test(@name, \'beta$\'))]')
        meta['date'] = '/parent::b/text()'
        meta['url-xpath'] = '/@href'
        meta['version'] = '/@name'
        return super().parse(response)

    def first_request(self, data):
        return 'http://www.aquamaniac.de/sites/download/packages.php?' \
               'package={}&showall=1'.format(data['package'])
