#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heading
*******
About this module...


Contents
********
    * :func:`fname2metadata()`: Extracts metadata from a filename.
    * :func:`metadata2fname()`: Generates filename from metadata.
    * :func:`rearrange_filename()`: Changes file_format {author}_{title} to {title}_{format}
    * :func:`readMetadataFromCsv()`: reads metadata from CSV-file.
    * :func:`path_smart_rename()`: renames files to filenames that can include folders.
"""

import json
import logging
import os
import re
import csv
from parse import *
import pandas as pd
from lxml import etree

log = logging.getLogger(__name__)


def fname2metadata(fname, pattern='{author}_{title}'):
    """Extract metadata from a filename.
    
    With this function you can create a dictionary containing metadata.
    Only the filename's basepath without any extensions will be considered.
    Furthermore, you have to specifiy the pattern of the filename.
    
    Args:
        fname (str): The name of a text file, with or without path as prefix
            and extension as suffix, respectively.
        pattern (str), optional: The filename's pattern. Write describing tokens
            within braces, those will be you dictionary's keys. Defaults to
            ``{author}_{title}``.
    
    Returns:
        A ``Result`` object (instanced by :module:`parse`), meaning an ordered
        dictionary with describers as keys and metadata as values.
    
    Todo:
        * Find an appropriate exception instance.
        
    Example:
        >>> fname = 'corpus/Goethe_Stella.txt'
        >>> pattern = '{author}_{title}'
        >>> fname2metadata(fname=fname,
        ...                pattern=pattern) # doctest: +NORMALIZE_WHITESPACE
                                  author   title
        corpus/Goethe_Stella.txt  Goethe  Stella

    """
    log.debug("Extracting metadata from filename '{0}' with pattern '{1}' ...".format(fname, pattern)) 
    basename, _ = os.path.splitext(os.path.basename(fname))
    metadata = parse(pattern, basename)
    if metadata is not None:
        return pd.DataFrame(metadata.named, index=[fname])
    else:
        raise ValueError("The pattern '{0}' did not match the structure of '{1}'.".format(pattern, fname))


def metadata2fname(dataset, pattern='{author}_{title}'):
    """Construct a filename from a metadata set and a pattern.
    
    Args:
        dataset (dict-like): A metadata set, referenced keys subscriptable.
        pattern (str), optional: a general pattern for the desired filename.
            Data keys between braces. Default to "{author}_{title}". 

    Returns:
        A string.
    """
    return pattern.format_map(dataset)


def metadata2csv(dataset, fname, **kwargs):
    """Writes metadata to CSV-file.
    
    With this function, you can write metadata 
    
    Args:
        datamodel (pd.DataFrame): A pandas DataFrame containing metadata, where
            each row stands for one document.
        fname (str): Filename for CSV-file.
    
    Returns:
        None
    """
    dataset.to_csv(fname, **kwargs)
    
    
def readMetadataFromCsv(datalocation, datafieldnames = None, **kwargs):
    '''Reads CSV-file to datamodel.
    
    With this function, you can read metadata information from a csv file.
    
    Args:
        datalocation (str): a string defining where to finde the CSV-file
        datafieldnames (list or None): if None, the values of the first line of the file are used as fildnames; alternativly you can define a list of fildnames
        further args get handet over to func csv.DictReader
    
    Returns: a list of dicts; each dict representing the data of one document
        
    '''

    corpusdata = []
    with open(datalocation, newline = '') as csvfile:
        tablereader = csv.DictReader(csvfile, fieldnames = datafieldnames, **kwargs)
        for row in tablereader:
            corpusdata.append(row) 

    ##Auf mögliche Eingabefehler hinweisen
    if len(corpusdata) == 0:
        log.warning("CSV-File is empty.")
    elif len(corpusdata[0]) == 1:
        log.warning("CSV-File has only 1 column. Please check delimiter.")

    return corpusdata
    
def path_smart_rename(old_fname, new_fname):
    """Renames a file from old_fname to new_fname & deals with paths in names.
    
    Args:
        old_fname: A string describing the path to the file to be renamed.
        new_fname: A string describing the desired new filename and location.

    Returns:
        –
    """
    old_dirs, _ = os.path.split(old_fname)
    new_dirs, _ = os.path.split(new_fname)
    if new_dirs:
        os.makedirs(new_dirs, exist_ok=True)
    os.rename(old_fname, new_fname)
    if old_dirs:
        try:
            os.removedirs(old_dirs)
            log.info('Recursively removed empty directories from {0}.'.format(old_dirs))
        except OSError:
            log.debug('Failed removing {0} recursively because it’s not empty.'.format(old_dirs))

def read_sidecar(fname):
    """Read metadata from sidecar file.

    Args:
        fname (str): A filename.

    Returns:
        A metadata dict. It carries an extra key `_from` with value 'sidecar'.
        Raises IOError if there is no sidecar file.
    """
    sc_fname = os.path.splitext(fname)[0]+'.json'
    with open(sc_fname) as f:
        dataset = json.load(f)
    dataset['_from'] = 'sidecar'
    return dataset

def write_sidecar(dataset):
    """Write metadata to a sidecar file.

    Args:
        dataset (dict): A metadata set.

    Returns:
        --
    """
    sc_fname = os.path.splitext(dataset['filename'])[0]+'.json'
    prepared_dataset = {k:v for k, v in dataset.items() if k != '_from'}

    with open(sc_fname, 'w') as f:
        json.dump(prepared_dataset, f)

def renameCorpusFiles(metalist, fields, seperator):
    """Takes metadata fields and creates new filenames for corpus files

    Args:
        metalist: List of dicts containing meatdatainforamtion and at least a field for filenames
        fields: List of fields to be used for new filenames
        seperator: String to separte different fields in new filenames

    Returns:
        updated list of dicts with containing new filenames

    To Do:
        * Warning for missing values in given fields?
        * Option to set placeholder for these missing values
    """
    updated_metalist = list()
    # iterate over meta_dicts
    for meta_dict in metalist:

        # get file extension
        try:
            file_extension = os.path.splitext(meta_dict["filename"])[1]
        except KeyError:
            log.debug('Missing field \'filename\' in metadata.'.format(meta_dict))

        # get path
        path = os.path.dirname(meta_dict["filename"])

        new_filename = ""
        #  iterate over field_pattern
        for field in fields:
            try:
                new_filename += str(meta_dict[field]) + str(seperator)
            except KeyError:
                log.debug('Field is not defined in metadata:'.format(field))
            
        # remove last seperator
        new_filename = re.sub(re.escape(seperator) + "$", "", new_filename)
        # join to path+extention
        new_filename = os.path.join(path, new_filename) + file_extension

        # rename file
        path_smart_rename(meta_dict["filename"], new_filename)

        # update meta_dict
        meta_dict["filename"] = new_filename
        updated_metalist.append(meta_dict)

    return updated_metalist


def read_meta_from_tei(filepaths, element_dict, namespace):
    """Takes metadata fields and creates new filenames for corpus files

        Args:
            filepaths: List of filepaths
            element_dict: List of Elements containing metadata
            namespace: namespace of xml document as dict

        Returns:
            updated list of dicts with containing new filenames

        To Do:
            * Warning for missing values in given fields?
            * Option to set placeholder for these missing values
        """
    element_dict.update({"filepath": ""})
    meta_frame = pd.DataFrame(columns=(list(element_dict.keys())))
    for filepath in filepaths:
        with open(filepath, "rb") as teidoc:
            content = teidoc.read()

        tei = etree.fromstring(content)
        meta_dict = {"filepath": filepath}

        for element in element_dict.keys():

            if element == "filepath":
                continue
            meta_value = tei.xpath("//tei:TEI/tei:teiHeader//tei:" + str(element) + "/text()", namespaces=namespace)
            if len(meta_value) < 1:
                meta_value = None
                log.warning('Missing value for field \'' + element + '\' in TEI document: ' + str(filepath))

            meta_dict.update({element: meta_value})
        meta_frame_single = pd.DataFrame(meta_dict)
        meta_frame = meta_frame.append(meta_frame_single)

    return meta_frame
