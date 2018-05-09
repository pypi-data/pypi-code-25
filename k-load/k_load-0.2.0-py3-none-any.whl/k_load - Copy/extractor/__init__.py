from urllib import request


class DownloadableObj:
    web_url = ''
    site = ''
    file_url = ''
    filename = ''
    title = ''
    author = ''
    format = ''
    type = ''
    size = ''

    def __init__(self, website_url):
        self.web_url = website_url

    def __repr__(self):
        return self.filename

    def get_data(self):
        raise NotImplementedError('This depends on specific object types. ')

    def set_data(self, file_url, title, author, format, type, size):
        self.file_url = file_url
        self.filename = title+' - '+author+format
        self.title = title
        self.author = author
        self.format = format
        self.type = type
        self.size = size

    def download(self):
        request.urlretrieve(self.file_url, self.filename)

    def log(self):
        print('——————————————————————————————')
        print('\t\tK - Download                ')
        print('——————————————————————————————')
        print('- Site: \t', self.site)
        print('- Title: \t', self.title)
        print('- Stream: \t')
        print('    - type: \t', self.type)
        print('    - format: \t', self.format)
        print('    - size: \t', self.size)
        print('')
        print('downloading...' + self.filename)
        print('███████████(进度条未实现)')

    def exec(self):
        self.get_data()
        self.log()
        self.download()
