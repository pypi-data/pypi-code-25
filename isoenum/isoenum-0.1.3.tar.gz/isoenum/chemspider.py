#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

POST /InChI.asmx/InChIToMol HTTP/1.1
Host: www.chemspider.com
Content-Type: application/x-www-form-urlencoded
Content-Length: length

inchi=string

"""

import os
import sys
import json
import xml.etree.ElementTree as ET

import requests
import pdir

with open("{}/conf/chemspider.json".format(os.path.abspath(os.path.dirname(__file__))), "r") as infile:
    chemspider_conf = json.load(infile)


def inchi_to_mol(inchi, chemspider_conf):
    """Convert from inchi string or file to molfile string or file. 
    
    :param inchi: InChI string or path to file containing InChI string.
    :param str url: URL path to  
    :param dict chemspider_conf:
    :return: 
    :rtype: str
    """
    if os.path.exists(inchi):
        with open(inchi, 'r') as inf:
            inchi = inf.read().strip()

    if not inchi.startswith('InChI='):
        inchi = 'InChI={}'.format(inchi)

    url = chemspider_conf['inchi_to_mol']['url']
    headers = chemspider_conf['inchi_to_mol']['headers']
    payload = {'inchi': inchi}

    r = requests.post(url, data=payload, headers=headers)

    if r.ok:
        root = ET.fromstring(r.text)
        return root.text
    return ""


def mol_to_inchi(inchi):
    pass


if __name__ == '__main__':
    script = sys.argv.pop(0)
    inchi = sys.argv.pop(0)

    mol_str = inchi_to_mol(inchi, chemspider_conf)
    print(mol_str)