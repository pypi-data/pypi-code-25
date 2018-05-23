import os.path
import sys
import json

from excel_to_json.book import Book


def convert_xlsl(excel_file):
    print('converting %s'%excel_file)
    file_dir = os.path.dirname(excel_file)
    workbook = Book()
    workbook.parse_file(excel_file)
    return workbook.out_file(file_dir)


def convert_folder(folder_path):
    outfile_paths = []
    paths = os.listdir(folder_path)
    for path in paths:
        if os.path.isdir(path):
            outfile_paths.extend(convert_folder(path))
        elif os.path.isfile(path) and path.endswith('.xlsx'):
            outfile_paths.extend(convert_xlsl(path))
    return outfile_paths


def excel_to_json():
    input_paths = sys.argv[1:]
    outfile_paths = []
    for path in input_paths:
        if os.path.isdir(path):
            outfile_paths.extend(convert_folder(path))
        elif os.path.isfile(path) and path.endswith('.xlsx'):
            outfile_paths.extend(convert_xlsl(path))
    return outfile_paths
