from . import git_service_url, GitSpider


class GitLab(GitSpider):
    name = 'gitlab'

    def parse(self, response):
        if self.searching_commits(response):
            for li in response.xpath(
                    '//ul[re:test(@class, \'\\bcommit-list\\b\')]//li'):
                commit_link = li.xpath(
                    './/a[re:test(@class, \'\\bcommit-row-message\\b\')]')
                message = commit_link.xpath('./text()').extract_first().strip()
                item = self.item(response, message)
                if not item:
                    continue
                item['date'] = li.xpath('.//time/@datetime').extract_first()
                item['url'] = response.urljoin(
                    commit_link.xpath('./@href').extract_first())
                return item
        else:
            for span in response.xpath(
                    '//a[re:test(@class, \'\\bitem-title\\b\')]'):
                tag = ' '.join(item.strip() for item in
                               span.xpath('./text()').extract()).strip()
                item = self.item(response, tag)
                if not item:
                    continue
                item['date'] = span.xpath('./following-sibling::div'
                                          '//time/@datetime').extract_first()
                assert item['date'] is not None
                item['url'] = response.urljoin(
                    span.xpath('../@href').extract_first())
                return item
        raise NotImplementedError  # Multi-page support

    def first_request(self, data):
        super().first_request(data)
        return git_service_url('https://gitlab.com/{project}/{repository}',
                               data, '/commits/master', '/tags')
