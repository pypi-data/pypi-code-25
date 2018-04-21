# -*- coding: utf-8 -*-

"""Writes a nested list to a CSV file"""

import csv

##########################################
##########################################
##########################################
##########################################


def write_to_csv(destination_file, content, delim=','):

    with open(destination_file, 'w', encoding='UTF-8', newline='') as f:

        writer = csv.writer(f, delimiter=delim)

        writer.writerows(content)

        f.close()
