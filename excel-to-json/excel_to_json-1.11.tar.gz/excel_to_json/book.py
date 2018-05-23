import os
import json

from openpyxl import load_workbook
from excel_to_json.sheet import Sheet
import excel_to_json.columntitle as columntitle
import excel_to_json.sheetname as sheetname
from excel_to_json.date_encoder import DateEncoder


class Book:
    def __init__(self):
        self.sheets = []

    def parse_file(self, file_path):
        wb = load_workbook(file_path)
        for ws in wb:
            sheet = Sheet(ws.title)
            sheet.parse(ws)
            self.sheets.append(sheet)
        # deal the joint
        for sheet in self.sheets:
            for target, join in sheet.get_joins().items():
                target_sheet_name = columntitle.join_target_sheet(target)
                target_column = columntitle.join_target_column(target)
                target_sheet = self.get_sheet(target_sheet_name)
                for join_identify, datas in join.items():
                    setter = target_sheet.get_anchor_setter(target_column, join_identify)
                    if setter:
                        for data in datas:
                            setter(data)

    def out_file(self, path):
        outfile_paths = []
        # check predefined out file suffix, like .json or .yaml
        data = None
        for sheet in filter(lambda s: sheetname.is_outfile(s.title), self.sheets):
            try:
                data = self.get_data(sheet)
                outfile_path = os.path.join(path, sheetname.out_file_name(sheet.title.strip('!')))
                f = open(outfile_path, 'w+', encoding='utf-8')
                f.write(data)
                f.close()
                outfile_paths.append(outfile_path)
            except Exception as err:
                print(err)
        return outfile_paths

    def out_console(self):
        # check predefined out file suffix, like .json or .yaml
        data = None
        for sheet in self.sheets:
            try:
                data = self.get_data(sheet)
                print(data)
            except Exception as err:
                print(err)

    def get_sheet(self, sheet_name):
        return next(filter(lambda s: sheetname.shortname(s.title) == sheet_name, self.sheets), None)

    @staticmethod
    def get_data(sheet):
        data = None
        if sheetname.is_json(sheet.title):
            data = Book.get_json_data(sheet)
        # can add yaml support
        return data

    @staticmethod
    def get_json_data(sheet):
        datas = sheet.get_data()
        if sheetname.is_array(sheet.title):
            data = json.dumps(datas, cls=DateEncoder, ensure_ascii=False)
        else:
            if len(datas) == 0:
                data = '{}'
            else:
                data = json.dumps(sheet.get_data()[0], cls=DateEncoder, ensure_ascii=False)
        return data

