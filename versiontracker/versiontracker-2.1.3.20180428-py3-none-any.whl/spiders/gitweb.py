from scrapy import Request

from . import GitSpider


class GitWeb(GitSpider):
    name = 'gitweb'

    def _iter_shortlog(self, response, base_xpath):
        for tr in response.xpath(
                '//table[re:test(@class, \'\\bshortlog\\b\')]//tr'):
            message = tr.xpath(
                './/{}//a/text()'.format(base_xpath)).extract_first().strip()
            item = self.item(response, message)
            if not item:
                continue
            item['date'] = tr.xpath('.//td[1]//text()').extract_first()
            item['url'] = response.urljoin(tr.xpath(
                './/{}//a/@href'.format(base_xpath)).extract_first())
            yield item

    def parse(self, response):
        if response.meta.get('branch', None):
            for item in self._iter_shortlog(
                    response, 'span[re:test(@class, "\\btag\\b")]'):
                return item
        elif self.searching_commits(response):
            for item in self._iter_shortlog(response, 'td[3]'):
                return item
        else:
            for tr in response.xpath(
                    '//table[re:test(@class, \'\\btags\\b\')]//tr'):
                commit_link_selector = tr.xpath('.//td[2]//a')
                tag = commit_link_selector.xpath(
                    './text()').extract_first().strip()
                item = self.item(response, tag)
                if not item:
                    continue
                tag_link = tr.xpath('.//td[4]//a/@href').extract_first()
                if tag_link is not None:
                    item['url'] = response.urljoin(tag_link)
                else:
                    item['url'] = response.urljoin(commit_link_selector.xpath(
                        './@href').extract_first())
                response.meta['item'] = item
                return Request(
                    item['url'], callback=self.parse_date, meta=response.meta)
        raise NotImplementedError  # Multi-page support

    @staticmethod
    def parse_date(response):
        item = response.meta['item']
        xpath = '//span[re:test(@class, \'\\bdatetime\\b\')]/text()'
        date = response.xpath(xpath).extract_first()
        if not date:
            xpath = '//table[re:test(@class, \'\\bobject_header\\b\')]' \
                    '//tr[re:test(td[1]/text(), \'^\\s*$\')]/td[2]/text()'
            date = response.xpath(xpath).extract_first()
        item['date'] = date
        return item

    def first_request(self, data):
        super().first_request(data)
        branch, commit = data.get('branch', None), data.get('commit', None)
        url = data['url'].rstrip('/')
        parameter_prefix = '&a=' if '?' in url else '/'
        if branch:
            suffix = 'shortlog/refs/heads/{}'.format(branch)
        elif commit:
            suffix = 'shortlog'
        else:
            suffix = 'tags'
        return url + parameter_prefix + suffix
