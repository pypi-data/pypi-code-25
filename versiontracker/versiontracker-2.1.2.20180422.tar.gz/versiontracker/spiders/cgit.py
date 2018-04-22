from scrapy import Request

from . import GitSpider


class CGit(GitSpider):
    name = 'cgit'

    def parse(self, response):
        searching_commits = self.searching_commits(response)
        link_xpath = './/td[{}]//a'.format(
            2 if searching_commits else 1)
        for tr in response.xpath(
                '//table[re:test(@class, \'\\blist\\b\')]//tr')[1:]:
            link_selector = tr.xpath(link_xpath)
            string = link_selector.xpath('./text()').extract_first().strip()
            item = self.item(response, string)
            if item:
                item['url'] = response.urljoin(
                    link_selector.xpath('./@href').extract_first())
                if searching_commits:
                    item['date'] = tr.xpath(
                        './/td[1]//span/@title').extract_first()
                else:
                    date = tr.xpath('.//td[4]//span/@title').extract_first()
                    if not date:
                        response.meta['item'] = item
                        return Request(response.urljoin(item['url']),
                                       callback=self.parse_date,
                                       meta=response.meta)
                    else:
                        item['date'] = date
                return item
        raise NotImplementedError  # Multi-page support

    @staticmethod
    def parse_date(response):
        item = response.meta['item']
        item['date'] = response.xpath(
            '//table[re:test(@class, \'\\bcommit-info\\b\')]'
            '//tr[2]//td[2]/text()').extract_first()
        return item

    def first_request(self, data):
        super().first_request(data)
        return data['url'].rstrip("/") + (
            '/log/' if data.get('commit', None) else '/refs/tags')
