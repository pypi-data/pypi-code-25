#!/usr/bin/python3
# coding: utf-8

"""
Pandoc filter to extract code blocs  
"""

##
## Constants
##
DEST="./codeblocks/"
DEFAULT_EXTENSION="md"

EXTENSIONS={}
EXTENSIONS['python']="py"  
EXTENSIONS['console']="sh" 
EXTENSIONS['bash']="sh"
EXTENSIONS['yaml']="yml"
EXTENSIONS['sql']="sql"
EXTENSIONS['sqlpostgresql']="sql"
# ADD NEW FILE EXTENSIONS HERE 


from panflute import *
import json
import sys
import os


def prepare(doc):
    # pec means Pandoc Extract Code
    doc.pec_current_header=''
    doc.pec_files={}


def search_code_blocks(elem, doc):
    if type(elem) == Header:
        doc.pec_current_header=stringify(elem)
        doc.pec_current_header=elem.identifier
        

    if type(elem) == CodeBlock :
        # we ignore code block with no language specified
        if elem.classes:
            export(elem,doc)
            
            
##
## Create a file and write the code in it
##   - elem is CodeBock elem
def export(elem,doc):
    filename="" # 
    if 'filename' in elem.attributes:
        # writer can define the filename
        # for each code block
        filename = elem.attributes['filename']
    else: 
        filename = doc.pec_current_header
        # increment the filname
        # A section may have multiple code blocks 
        doc.pec_current_header+='_'
        # Add the extensions
        language=elem.classes[0]
        if language in EXTENSIONS:
            filename+='.' + EXTENSIONS[language]
        else:
            filename+='.' + DEFAULT_EXTENSION
        
    doc.pec_files[filename]=elem.text
    debug(filename)



def finalize(doc):
    debug("------- FOUND %d CODE BLOCKS -------" % len(doc.pec_files))
    
    # TODO : find a way to get the directory of the output file
    dest=DEST
    if not os.path.exists(dest):
        os.makedirs(dest)
        
    # Write the files in the directory
    for filename, content in doc.pec_files.items():
        path=os.path.join(dest,filename)
        file = open(path,"w") 
        file.write(content)
        file.close
        debug("exported %s" % path)

def main(doc=None):
    return run_filter(  search_code_blocks, 
                        prepare=prepare, 
                        finalize=finalize, 
                        doc=doc)

if __name__ == "__main__":
    main()
