from unittest import TestCase
from Db import Db
from pymongo import MongoClient

URL = u'testurl'
TITLE = u'test title'
TAGS = u'test tags'
BODY = u'test body'

test_client = MongoClient()
test_db = test_client.test
my_db = Db('localhost', 27017, 'test')


class TestDb(TestCase):
    def delete_document(self, my_url=URL):
        """
        Helper function to delete a document from the database
        :param my_url:
        :return: True or False depending if the delete was successful
        """
        result = test_db.test.delete_one({'url': my_url})
        if result is not None:
            return True
        return False

    def create_document(self, my_url=URL, my_title=TITLE, my_tags=TAGS, my_body=BODY):
        """
        Helper function to create a document in the database with parameters
        :param my_url:
        :param my_title:
        :param my_tags:
        :param my_body:
        :return: True or False depending if the insert was successful
        """
        result = test_db.test.insert_one({'url': my_url, 'title': my_title, 'tags': my_tags, 'body': my_body})
        if result is None:
            return False
        return True

    def get_document(self, my_url=URL):
        return test_db.test.find_one({'url': my_url})

    def exists_document(self, my_url=URL):
        """
        Helper function to check the existence of a document in the database.
        :param my_url:
        :return: True or False whether the document exists or not
        """
        result = self.get_document(my_url)
        if result is None:
            return False
        return True

    def test_insert(self):
        """
        Tests if the given content to a document is valid
        :return:
        """
        my_db.insert({'url': URL, 'title': TITLE, 'tags': TAGS, 'body': BODY})
        result = self.get_document()
        assert result is not None
        assert URL in result['url']
        assert TITLE in result['title']
        assert TAGS in result['tags']
        assert BODY in result['body']

    def test_exists(self):
        """
        Test if a given url exists or doesn't
        :return:
        """
        result = my_db.exists(URL)
        assert result is False
        self.create_document()
        result = my_db.exists(URL)
        assert result is True

    def test_convert(self):
        self.fail()

    def tearDown(self):
        """
        Delete every document in the database
        :return:
        """
        test_db.test.delete_many({})
