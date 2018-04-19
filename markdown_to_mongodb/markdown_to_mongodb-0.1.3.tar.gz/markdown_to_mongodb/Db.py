# -*- coding: utf-8 -*-
from pymongo import MongoClient
import os
from Document import Document
import argparse


class Db(object):
    def __init__(self, ip='localhost', port=27017, collection_name=''):
        self.collection_name = collection_name
        self.client = MongoClient(ip, port)
        self.db = self.client[self.collection_name]
        self.success_log = []
        self.fail_log = []

    def try_catch(func):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                print str(e)
        return wrapped

    @try_catch
    def insert(self, my_dict):
        """
        Performs an insert on the MongoDB instance. The dictionary can contain
        anything but must have a url.
        :param my_dict: The processed contents of the markdown file in a
                        dictionary.
        :return: True or False depending if the insert was successful.
        """
        result = self.db[self.collection_name].insert_one(my_dict)
        if result.inserted_id == "":
            return False
        return True

    def convert(self, folder):
        """
        Loops through a supplied folder path looking for markdown files. If it
        finds files with extension .md, the file will be processed into meta
        and body from process_markdown method. After that data is inserted
        into the database.
        :param folder: path to the markdown directory.
        """
        for root, dirs, files in os.walk(folder):
            for file_ in files:
                if file_.endswith('.md'):
                    my_doc = Document(os.path.join(root, file_))
                    data = my_doc.process_markdown()
                    if self.insert(data):
                        self.success_log.append(os.path.join(root, file_))
                    else:
                        self.fail_log.append(os.path.join(root, file_))

    def print_report(self):
        """
        Creates a report of the successes and failures of converting markdown
        files and inserting them into MongoDB.
        """
        def my_print(my_message, my_list):
            if my_list is not None and len(my_list) > 0:
                print(my_message)
                for i in my_list:
                    print("\t{}\n".format(i))

        my_print('Successfully converted and inserted:\n', self.success_log)
        my_print('Could not convert and insert:\n', self.fail_log)


def handle_args():
    """
    Commandline arguments to insert a directory of markdown files into a
    MongoDB instance.
    ip: The ip address of your mongodb instance. Default localhost.
    port: The port of your mongodb instance. Default 27017.
    collection: The name of the collection you want to insert your
                documents into.
    directory: The directory containing your markdown files to insert.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("ip",
                        help="The ip address of your mongodb \
                         instance. Default localhost.")
    parser.add_argument("port", type=int,
                        help="The port of your mongodb instance. \
                        Default 27017.")
    parser.add_argument("collection",
                        help="The name of the collection you want \
                        to insert your documents into.")
    parser.add_argument("directory",
                        help="The directory containing your markdown \
                        files to insert.")
    args = parser.parse_args()

    collection_name = args.collection
    markdown_directory = args.directory
    ip = args.ip
    port = args.port
    my_db = Db(ip, port, collection_name)
    my_db.convert(markdown_directory)
    my_db.print_report()


if __name__ == '__main__':
    handle_args()
