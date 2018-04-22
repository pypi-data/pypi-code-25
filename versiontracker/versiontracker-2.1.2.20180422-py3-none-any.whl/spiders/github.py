from scrapy import Request

from . import git_service_url, GitSpider


class GitHub(GitSpider):
    name = 'github'

    def parse(self, response):
        if self.searching_commits(response):
            for li in response.xpath(
                    '//li[re:test(@class, \'\\bcommit\\b\')]'):
                commit_link = li.xpath(
                    './/a[re:test(@class, \'\\bmessage\\b\')]')
                message = commit_link.xpath('./text()').extract_first().strip()
                item = self.item(response, message)
                if not item:
                    continue
                item['date'] = li.xpath(
                    './/relative-time/@datetime').extract_first()
                item['url'] = response.urljoin(
                    commit_link.xpath('./@href').extract_first())
                return item
        elif '/releases' not in response.url:
            for tr in response.xpath('//table[re:test(@class, '
                                     '\'\\breleases-tag-list\\b\')]//tr'):
                tag_selector = tr.xpath(
                    './/span[re:test(@class, \'\\btag-name\\b\')]')
                tag = tag_selector.xpath('./text()').extract_first().strip()
                item = self.item(response, tag)
                if not item:
                    continue
                item['date'] = tr.xpath(
                    './/relative-time/@datetime').extract_first()
                item['url'] = response.urljoin(
                    tag_selector.xpath('../@href').extract_first())
                return item
        else:
            if not response.url.endswith('/releases'):
                item = self.item(response, response.url.split("/")[-1])
                if item:
                    item['date'] = response.xpath(
                        '//relative-time/@datetime').extract_first()
                    return item
            return Request(self._url(response.meta, ignore_latest=True),
                           meta=response.meta)
        raise NotImplementedError  # Multi-page support

    @staticmethod
    def _url(data, ignore_latest=None):
        if ignore_latest is None:
            ignore_latest = data.get('ignore-latest', False)
        tag_suffix = '/tags' if ignore_latest else '/releases/latest'
        return git_service_url('https://github.com/{project}/{repository}',
                               data, '/commits', tag_suffix)

    def first_request(self, data):
        super().first_request(data)
        return self._url(data)
