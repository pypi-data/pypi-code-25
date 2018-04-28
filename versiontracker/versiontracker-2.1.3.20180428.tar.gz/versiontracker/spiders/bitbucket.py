from . import git_service_url, GitSpider


class Bitbucket(GitSpider):
    name = 'bitbucket'

    def parse(self, response):
        searching_commits = bool(self.searching_commits(response))
        for tr in response.xpath(
                '//tr[re:test(@class, \'\\biterable-item\\b\')]'):
            if searching_commits:
                message = tr.xpath('.//td[re:test(@class, \'\\btext\\b\')]'
                                   '/text()').extract_first().strip()
            else:
                message = tr.xpath('.//td[re:test(@class, \'\\bname\\b\')]'
                                   '/text()').extract_first().strip()
                if message == 'tip':
                    continue
            item = self.item(response, message)
            if not item:
                continue
            item['date'] = tr.xpath('.//time/@datetime').extract_first()
            item['url'] = response.urljoin(tr.xpath(
                './/a[re:test(@class, \'\\bhash\\b\')]'
                '/@href').extract_first())
            return item
        raise NotImplementedError  # Multi-page support

    def first_request(self, data):
        super().first_request(data)
        return git_service_url(
            'https://bitbucket.org/{project}/{repository}', data,
            '/commits/branch/default', '/downloads?tab=tags')
