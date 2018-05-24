import isatools.isatab as isatab
import os

__author__ = 'nsadawi'


def exploreISA(pathToISATABFile, verbose=True):
    """
    This function loops through the ISATAB file and lists its Studies and their associated Assays.
    :param pathToISATABFile: The path to the ISATAB file.
    :type xpathToISATABFile: str
    :param verbose: Whether (or not) to print out details of Studies and Assays (default: True)
    :type verbose: boolean
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    try:
        isa_tab_record = isatab.load(pathToISATABFile, skip_load_tables=True)
        if verbose:
            print('In this ISATAB file you have:')
            for idx,st in enumerate(isa_tab_record.studies):
                print('Study: '+str(idx+1))
                print('\tStudy Identifier: '+st.identifier+', Study ID: '+st.id+', Study Filename: '+st.filename+', Study Title: '+st.title)
                print('\tThis Study has the following Assays:')
                for ix,a in enumerate(st.assays):
                    print('\tAssay: '+str(ix+1))
                    print('\t\tAssay Filename: '+a.filename+', Assay technology type: '+a.technology_type.term)
    except FileNotFoundError as err:
        raise err

def getISAAssay(assayNum, studyNum, pathToISATABFile):
    """
    This function returns an Assay object given the assay and study numbers in an ISA file
    Typically, you should use the exploreISA function to check the contents
    of the ISA file and retrieve the assay and study numbers you are interested in!
    :param assayNum: The Assay number (notice it's not zero-based index).
    :type assayNum: int
    :param studyNum: The Study number (notice it's not zero-based index).
    :type studyNum: int
    :param pathToISATABFile: The path to the ISATAB file
    :type pathToISATABFile: str
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    from isatools import isatab
    import copy
    try:
        isa = isatab.load(pathToISATABFile, skip_load_tables=True)
        std = isa.studies[studyNum - 1]
        return copy.deepcopy(std.assays[assayNum - 1])
    except FileNotFoundError as err:
        raise err

def getISAStudy(studyNum, pathToISATABFile, noAssays = True):
    """
    This function returns a Study object given the study number in an ISA file
    Typically, you should use the exploreISA function to check the contents
    of the ISA file and retrieve the study number you are interested in!
    :param studyNum: The Study number (notice it's not zero-based index).
    :type studyNum: int
    :param pathToISATABFile: The path to the ISATAB file
    :type pathToISATABFile: str
    :param noAssays: whetehr to remove all assays (i.e. return a copy of the study only)
    :type noAssays: boolean
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    from isatools import isatab
    import copy
    try:
        isa = isatab.load(pathToISATABFile, skip_load_tables=True)
        st = copy.deepcopy(isa.studies[studyNum - 1])
        if noAssays:
            st.assays = []
        return st
    except FileNotFoundError as err:
        raise err

def appendStudytoISA(study, pathToISATABFile):
    """
    This function appends a Study object to an ISA file
    Typically, you should use the exploreISA function to check the contents
    of the ISA file!
    :param study: The Study object.
    :type study: ISA Study object
    :param pathToISATABFile: The path to the ISATAB file
    :type pathToISATABFile: string
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    from isatools import isatab
    import os
    try:
        isa = isatab.load(pathToISATABFile, skip_load_tables=True)
        lngth = len(isa.studies)
        base = os.path.basename(study.filename)
        fname = os.path.splitext(base)[0]
        fname = fname + str(lngth)
        ext = os.path.splitext(base)[1]
        fname = fname + ext
        study.filename = fname
        isa.studies.append(study)
        isatab.dump(isa_obj=isa, output_path=pathToISATABFile)
    except FileNotFoundError as err:
        raise err

def appendAssayToStudy(assay, studyNum, pathToISATABFile):
    """
    This function appends an Assay object to a study in an ISA file
    Typically, you should use the exploreISA function to check the contents
    of the ISA file and retrieve the assay and study number you are interested in!
    :param assay: The Assay
    :type assay: ISA Assay object
    :param studyNum: The Study number (notice it's not zero-based index).
    :type studyNum: int
    :param pathToISATABFile: The path to the ISATAB file
    :type pathToISATABFile: string
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    from isatools import isatab
    try:
        isa = isatab.load(pathToISATABFile, skip_load_tables=True)
        std = isa.studies[studyNum - 1]
        lngth = len(std.assays)
        base  = os.path.basename(assay.filename)
        fname = os.path.splitext(base)[0]
        fname = fname + str(lngth)
        ext   = os.path.splitext(base)[1]
        fname = fname + ext
        assay.filename = fname
        isa.studies[studyNum - 1].assays.append(assay)
        isatab.dump(isa_obj=isa, output_path=pathToISATABFile)
    except FileNotFoundError as err:
        raise err

def dropAssayFromStudy(assayNum, studyNum, pathToISATABFile):
    """
    This function removes an Assay from a study in an ISA file
    Typically, you should use the exploreISA function to check the contents
    of the ISA file and retrieve the assay and study numbers you are interested in!
    :param assayNum: The Assay number (notice it's 1-based index).
    :type assayNum: int
    :param studyNum: The Study number (notice it's 1-based index).
    :type studyNum: int
    :param pathToISATABFile: The path to the ISATAB file
    :type pathToISATABFile: string
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    from isatools import isatab
    import os
    try:
        isa = isatab.load(pathToISATABFile, skip_load_tables=True)
        std = isa.studies[studyNum - 1]
        assays = std.assays
        if os.path.isfile(os.path.join(pathToISATABFile,assays[assayNum - 1].filename)):
            os.remove(os.path.join(pathToISATABFile,assays[assayNum - 1].filename))
        del assays[assayNum - 1]
        isatab.dump(isa_obj=isa, output_path=pathToISATABFile)
    except FileNotFoundError as err:
        raise err

def dropStudyFromISA(studyNum, pathToISATABFile):
    """
    This function removes a study from an ISA file
    Typically, you should use the exploreISA function to check the contents
    of the ISA file and retrieve the study number you are interested in!
    Warning: this function deletes the given study and all its associated assays
    :param studyNum: The Study number (notice it's 1-based index).
    :type studyNum: int
    :param pathToISATABFile: The path to the ISATAB file
    :type pathToISATABFile: string
    :raise FileNotFoundError: If pathToISATABFile does not contain file 'i_Investigation.txt'.
    """
    from isatools import isatab
    import os
    try:
        isa = isatab.load(pathToISATABFile, skip_load_tables=True)
        studies = isa.studies
        for assay in studies[studyNum - 1].assays:
            if os.path.isfile(os.path.join(pathToISATABFile,assay.filename)):
                os.remove(os.path.join(pathToISATABFile,assay.filename))
        if os.path.isfile(os.path.join(pathToISATABFile,studies[studyNum - 1].filename)):
            os.remove(os.path.join(pathToISATABFile,studies[studyNum - 1].filename))
        del studies[studyNum - 1]
        isatab.dump(isa_obj=isa, output_path=pathToISATABFile)
    except FileNotFoundError as err:
        raise err
