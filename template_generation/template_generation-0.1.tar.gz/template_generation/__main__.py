__author__ = 'I071034'
import os
from template_generation import processfile as pf

if __name__ == '__main__':
    # template.generate_new_template('source', 'target')
    rx = pf.ProcessFile(os.path.dirname(__file__),"source", "excel", "csv")
    rx.xml_to_excel()
    rx.excel_to_csv()
    # rx.xml_to_csv()