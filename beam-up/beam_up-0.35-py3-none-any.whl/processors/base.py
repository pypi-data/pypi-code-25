
class BaseProcessor(object):

    def translate(self, key, *args, **kwargs):
        return self.site.translate(self.language, key, *args, **kwargs)

    def file(self, filename):
        return self.site.request('static_file', filename)

    def href(self, href):
        return self.site.href(self.language, href)

    def __init__(self, site, params, language):
        self.site = site
        self.params = params
        self.language = language

    