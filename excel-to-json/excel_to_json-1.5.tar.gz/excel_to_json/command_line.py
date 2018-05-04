import os.path
import sys
import json

from excel_to_json.book import Book


def convert_xlsl(excel_file):
    file_dir = os.path.dirname(excel_file)
    workbook = Book()
    workbook.parse_file(excel_file)
    workbook.out_file(file_dir)


def convert_folder(folder_path):
    paths = os.listdir(folder_path)
    for path in paths:
        if os.path.isdir(path):
            convert_folder(path)
        elif os.path.isfile(path) and path.endswith('.xlsx'):
            convert_xlsl(path)


def excel_to_json():
    input_paths = sys.argv[1:]
    for path in input_paths:
        if os.path.isdir(path):
            convert_folder(path)
        elif os.path.isfile(path) and path.endswith('.xlsx'):
            convert_xlsl(path)
