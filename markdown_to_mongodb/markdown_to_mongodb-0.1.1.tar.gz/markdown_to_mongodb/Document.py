from collections import OrderedDict
from io import open
import os


class Document(object):
    def __init__(self, path):
        self.path = path
        self.content = ''
        self.meta = ''
        self.body = ''
        self.my_dict = OrderedDict()

    def process_markdown(self):
        """
        Driver that assigns this object's variables with the contents of the
        supplied markdown file, and returns a dictionary with the contents in
        key:value form.
        :return:
        """
        self.get_content()
        self.split_content()
        self.build_request()
        return self.my_dict

    def get_content(self):
        """
        Opens the file and reads it's data to this object's content variable.
        :return:
        """
        with open(self.path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def split_content(self):
        """
        Splits the content into two categories: meta and body.
        Metadata is at the top of the markdown like this:
        title: my title
        tags: my tags

        And body is the content after the metadata separated by two newlines.
        :return:
        """
        self.meta = self.content.split('\n\n', 1)
        self.body = self.meta[1]
        self.meta = self.meta[0]
        self.meta = self.meta.split('\n')

    def build_request(self):
        """
        Create a dictionary in key:value form from the meta and body variables.
        A url key:value is created from the markdown file's name.
        :return:
        """
        for line in self.meta:
            key = line.split(':', 1)[0].strip()
            value = line.split(':', 1)[1].strip()
            self.my_dict[key.lower()] = value.rstrip()
        self.my_dict[u'body'] = self.body.rstrip()
        filename = os.path.basename(self.path)
        self.my_dict[u'url'] = os.path.splitext(filename)[0].rstrip()
