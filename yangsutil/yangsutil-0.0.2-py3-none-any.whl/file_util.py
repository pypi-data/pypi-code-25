import os
import json
import csv
import yaml


class FileUtil:
    @staticmethod
    def make_folder(file_path):
        path_split = file_path.split('/')

        if len(path_split) > 1:
            dir_path = ''
            for path in path_split[:len(path_split) - 1]:
                dir_path += path + '/'

            if os.path.isdir(dir_path) is False:
                os.makedirs(dir_path)

        return file_path

    @staticmethod
    def read_file(file_path):
        try:
            f = open(file_path, 'r')
            data = f.read()
            f.close()
        except FileNotFoundError:
            return None

        return data

    @staticmethod
    def save_file(file_path, string_contents, is_append=False):
        FileUtil.make_folder(file_path)

        if is_append is True:
            f = open(file_path, 'a')
        else:
            f = open(file_path, 'w')

        f.write(string_contents)
        f.close()

    @staticmethod
    def read_json_file(file_path):
        raw = FileUtil.read_file(file_path=file_path)

        if raw is None:
            return None

        try:
            to_json = json.loads(raw)
        except json.decoder.JSONDecodeError:
            return None

        return dict(to_json)

    @staticmethod
    def save_json_file(file_path, dict_contents):
        if type(dict_contents) != dict:
            return None

        FileUtil.save_file(
            file_path=file_path,
            string_contents=json.dumps(dict_contents)
        )

    @staticmethod
    def save_csv_file(file_path, dict_list, fields_name=None):
        FileUtil.make_folder(file_path)

        if dict_list is None or type(dict_list) != list:
            return False

        fields_names = fields_name if fields_name is not None else dict_list[0].keys()

        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields_names)

            writer.writeheader()
            for dict_item in dict_list:
                writer.writerow(dict_item)

        return True

    @staticmethod
    def read_yml_file(file_path):
        raw = FileUtil.read_file(file_path=file_path)

        if raw is None:
            return None

        try:
            to_json = yaml.safe_load(raw)
        except yaml.YAMLError:
            return None

        return dict(to_json)
