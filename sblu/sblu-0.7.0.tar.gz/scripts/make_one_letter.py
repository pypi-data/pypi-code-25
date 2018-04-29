#!/usr/bin/env python3
import urllib.request
import gzip
import pprint
import re


url="http://ligand-expo.rcsb.org/dictionaries/Components-pub.cif.gz"

codes = dict()

with urllib.request.urlopen(url) as f:
    with gzip.GzipFile(fileobj=f) as f2:
        three_letter = None
        one_letter = None
        is_peptide = False
        for line in f2:
            if line.startswith(b'data_'):
                three_letter = line.split(b'_')[1].strip()
            if line.startswith(b'_chem_comp.type'):
                is_peptide = re.search(b'peptide', line, re.I) is not None
            if line.startswith(b'_chem_comp.one_letter_code'):
                one_letter = line.split()[1].strip()
                if one_letter != b'?' and is_peptide:
                    codes[three_letter.decode()] = one_letter.decode()


print('ONE_LETTER = {', end='')
for i, key in enumerate(sorted(codes)):
    if i % 5 == 0:
        print()
        print('   ', end='')
    print(" '{}': ".format(key), end='')
    print("'{}',".format(codes[key]), end='')
print()
print('}')
print()
print("""
def three_to_one(three_letter, single_only=False):
    one_letter = ONE_LETTER.get(three_letter, ' ')
    if single_only and len(one_letter) > 1:
        return ' '
    else:
        return one_letter
""")
