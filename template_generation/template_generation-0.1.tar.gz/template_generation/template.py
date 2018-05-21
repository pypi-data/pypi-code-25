import xml.etree.ElementTree as ET
from template_generation import processfile as pf
import os
from configparser import ConfigParser
import time
import datetime
import csv
import constant

def xml_parse(xml_file):
    """
    Parse an XML file, returns a tree of nodes and a dict of namespaces
    :param xml_file: the input XML file
    :returns: (doc, ns_map)
    """
    root = None
    ns_map = {}  # prefix -> ns_uri
    for event, elem in ET.iterparse(xml_file, ['start-ns', 'start', 'end']):
        if event == 'start-ns':
            # elem = (prefix, ns_uri)
            ns_map[elem[0]] = elem[1]
        elif event == 'start':
            if root is None:
                root = elem
    for prefix, uri in ns_map.items():
        ET.register_namespace(prefix, uri)

    return (ET.ElementTree(root), ns_map)

def generate_new_template_xml(sourcePath, targetPath):

    fileList = pf.get_file_list(pf.get_path_from_current(constant.os_path, sourcePath))
    for filename in fileList:
        sourceFile = pf.get_path_from_current(constant.os_path, sourcePath, filename)
        targetFile = pf.get_path_from_current(constant.os_path, targetPath, filename)
        with open (sourceFile, encoding='utf-8') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            for elem in root.iter():
                try:
                    elem.text = elem.text.replace('$999$', '001')
                    print(elem.text)
                except AttributeError:
                    pass
            tree.write(targetFile, encoding='utf-8')

def get_batch_num(config_parse, config_file):
    config_file = pf.get_path_from_current(constant.os_path, config_file)
    config_parse.read(config_file)
    batch_num = config_parse.get('BatchParam', 'Batch')
    return batch_num

def set_batch_num(config_parse, config_file, batch_num):
    config_file = pf.get_path_from_current(constant.os_path, config_file)
    config_parse.read(config_file)
    config_parse.set('BatchParam', 'Batch', batch_num)
    with open(config_file, 'w') as cf:
        config_parse.write(cf)

def generate_new_template(source_path, target_path, batch_value):
    config = ConfigParser()
    batch_num = batch_value
    if batch_value is None:
        batch_num = get_batch_num(config, constant.SETTING)

    fileList = pf.get_file_list(pf.get_path_from_current(constant.os_path, source_path))
    target_path = pf.get_path_from_current(constant.os_path, target_path, batch_value)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for filename in fileList:
        sourceFile = pf.get_path_from_current(constant.os_path, source_path, filename)
        targetFile = pf.get_path_from_current(target_path, filename)
        with open(sourceFile) as s:
            with open(targetFile, 'w+') as t:
                for line in s.readlines():
                    t.write(line.replace(constant.replace_txt, batch_num))
    batch_num_int = int(batch_num) + 1
    new_batch_num = str(batch_num_int).rjust(constant.replace_len, '0')
    set_batch_num(config, constant.SETTING, new_batch_num)

def generate_log(log_path, batch, user, comment):
    log_file = pf.get_path_from_current(constant.os_path,log_path, 'history.csv')
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    log_list = [batch, user, str(st), comment]
    with open(log_file, 'a', newline="") as f:
        c = csv.writer(f)
        # if len(f.readlines()) == 0:
        #     c.writerow('Batch,User,Datetime,Comment')
        c.writerow(log_list)

