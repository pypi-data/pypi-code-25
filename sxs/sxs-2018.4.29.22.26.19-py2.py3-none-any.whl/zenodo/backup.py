

def backup(catalog_file_name='complete_catalog.json', backup_directory='.'):
    """Back up all Zenodo records, including files

    * checksums - JSON file mapping checksums to file sizes and full paths relative to this file
    * catalog file - complete catalog JSON file, 
    * records - complete copies of each record in the 'sxs' Zenodo community
    * current - links named by SXS identifier pointing to current record directory
    * versions - links named by SXS identifier and version number pointing to corresponding record directory

    """
