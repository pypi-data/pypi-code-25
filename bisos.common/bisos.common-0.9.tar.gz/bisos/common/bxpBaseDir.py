# -*- coding: utf-8 -*-
"""\
*    *[Summary]* ::  A /library/ with ICM Cmnds to support ByStar bases creation facilities
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/de/bx/nne/dev-py/pypi/pkgs/unisos/icm2/dev/unisos/icm2/icm2.py :: [[elisp:(org-cycle)][| ]]
** is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
** *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
** A Python Interactively Command Module (PyICM). Part Of ByStar.
** Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
** Warning: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:


"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "bxpBaseDir"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712190917"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Production"
__status__ = "Production"
####+END:

__credits__ = [""]

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/icmInfo-mbNedaGpl.py"
icmInfo = {
    'authors':         ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"],
    'copyright':       "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]",
    'licenses':        ["[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"],
    'maintainers':     ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]",],
    'contacts':        ["[[http://mohsen.1.banan.byname.net/contact]]",],
    'partOf':          ["[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]",]
}
####+END:

####+BEGIN: bx:icm:python:topControls 
"""
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]] [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
"""
####+END:

"""
* 
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/pythonWb.org"
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "pep8 %s" (bx:buf-fname))))][pep8]] | [[elisp:(python-check (format "flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
####+END:
"""


####+BEGIN: bx:icm:python:section :title "ContentsList"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:func :funcName "insertPathForImports" :funcType "FrameWrk" :retType "none" :deco "" :argsList "path"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-FrameWrk  :: /insertPathForImports/ retType=none argsList=(path)  [[elisp:(org-cycle)][| ]]
"""
def insertPathForImports(
    path,
):
####+END:
    """
** Extends Python imports path with  ../lib/python
"""
    import os
    import sys
    absolutePath = os.path.abspath(path)    
    if os.path.isdir(absolutePath):
        sys.path.insert(1, absolutePath)

insertPathForImports("../lib/python/")



####+BEGIN: bx:dblock:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import os
import collections
import enum

# NOTYET, should become a dblock with its own subItem
from unisos import ucf
from unisos import icm

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__
# NOTYET DBLOCK Ends -- Rest of bisos libs follow


####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*
"""
####+END:

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "bxpBaseDir_LibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bxpBaseDir_LibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class bxpBaseDir_LibOverview(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        argsList=None,         # or Args-Input
    ):
        G = icm.IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        moduleDescription="""
*       [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]	Model and Terminology 					   :Overview:
*** bxpRootXxFile   -- /etc/bystarRoot, ~/.bystarRoot, /bystar
*** bxpRoot         -- Base For This Module
*** bpb             -- ByStar Platform Base, Location Of Relevant Parts (Bisos, blee, bsip
*** bpd             -- ByStar Platform Directory (Object), An instance of Class BxpBaseDir
**      [End-Of-Description]
"""
        
        moduleUsage="""
*       [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      [End-Of-Usage]
"""
        
        moduleStatus="""
*       [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/moduleOverview.py"
        cmndArgsSpec = {"0&-1": ['moduleDescription', 'moduleUsage', 'moduleStatus']}
        cmndArgsValid = cmndArgsSpec["0&-1"]
        icm.unusedSuppressForEval(moduleDescription, moduleUsage, moduleStatus)
        for each in effectiveArgsList:
            if each in cmndArgsValid:
                if interactive:
                    exec("""print({})""".format(each))
                
        return(format(str(__doc__)+moduleDescription))
####+END:


####+BEGIN: bx:dblock:python:section :title "Directory Base Locations"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Directory Base Locations*
"""
####+END:


####+BEGIN: bx:dblock:python:subSection :title "ByStar Root"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *ByStar Root*
"""
####+END:



####+BEGIN: bx:dblock:python:func :funcName "bxpRootBaseDirPtrSysFile_obtain" :comment "/etc/bystarRoot" :funcType "obtain" :retType "str" :argsList "" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bxpRootBaseDirPtrSysFile_obtain/ =/etc/bystarRoot= retType=str argsList=nil deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def bxpRootBaseDirPtrSysFile_obtain(
):
####+END:
    return os.path.abspath(
        "/etc/bisosRoot"
    )


####+BEGIN: bx:dblock:python:func :funcName "bxpRootBaseDirPtrUserFile_obtain" :comment "~/.bystarRoot" :funcType "obtain" :retType "str" :argsList "" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bxpRootBaseDirPtrUserFile_obtain/ =~/.bystarRoot= retType=str argsList=nil deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def bxpRootBaseDirPtrUserFile_obtain(
):
####+END:
    return os.path.abspath(
        os.path.expanduser(
            "~/.bisosRoot"
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "bxpRootBaseDirDefault_obtain" :comment "/bystar" :funcType "obtain" :retType "str" :argsList "" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bxpRootBaseDirDefault_obtain/ =~/.bystarRoot= retType=str argsList=nil deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def bxpRootBaseDirDefault_obtain(
):
####+END:
    # return os.path.abspath(
    #     "/bystar"
    # )
    return os.path.abspath(
        "/bisos"
    )


####+BEGIN: bx:dblock:python:subSection :title "BISOS Bases"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *BISOS Bases*
"""
####+END:


####+BEGIN: bx:dblock:python:func :funcName "bpbDist_baseObtain_bin" :comment "DIST BIN" :funcType "obtain" :retType "str" :argsList "baseDir" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbDist_baseObtain_bin/ =DIST BIN= retType=str argsList=(baseDir) deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def bpbDist_baseObtain_bin(
    baseDir,
):
####+END:
    """
** /bystar/dist/pip/bisos/bin
"""
    bxpRoot = bxpRoot_baseObtain(baseDir)            

    return( os.path.join(
        bxpRoot, "dist/pip/bisos", "bin"
    ))

####+BEGIN: bx:dblock:python:func :funcName "bpbDist_baseObtain_input" :comment "DIST DATA" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbDist_baseObtain_input/ =DIST DATA= retType=bool argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbDist_baseObtain_input(
    baseDir,
):
####+END:
    """
** /bystar/dist/pip/bisos/input
ICM packages and ICM Groups can keep their specific inputs, configuratios/etc. here.
"""
    bxpRoot = bxpRoot_baseObtain(baseDir)                

    return( os.path.join(
        bxpRoot, "dist/pip/bisos", "input"
    ))


####+BEGIN: bx:dblock:python:func :funcName "bpbBisos_baseObtain_bin" :comment "BISOS BIN" :funcType "obtain" :retType "str" :argsList "baseDir" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisos_baseObtain_bin/ =BISOS BIN= retType=str argsList=(baseDir) deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def bpbBisos_baseObtain_bin(
    baseDir,
):
####+END:
    bxpRoot = bxpRoot_baseObtain()            

    return( os.path.join(
        bxpRoot, "bisos", "bin"
    ))

####+BEGIN: bx:dblock:python:func :funcName "bpbBisos_baseObtain_input" :comment "BISOS DATA" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisos_baseObtain_input/ =BISOS DATA= retType=bool argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbBisos_baseObtain_input(
    baseDir,
):
####+END:
    bxpRoot = bxpRoot_baseObtain()                

    return( os.path.join(
        bxpRoot, "bisos", "input"
    ))


####+BEGIN: bx:dblock:python:subSection :title "BISOS Pkg Bases"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *BISOS Pkg Bases*
"""
####+END:


####+BEGIN: bx:dblock:python:func :funcName "bpbBisosPkg_baseObtain_var" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisosPkg_baseObtain_var/ retType=bool argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbBisosPkg_baseObtain_var(
    baseDir,
):
####+END:
    outcome = bxpRootGet().cmnd(
        interactive=False,
        baseDir=baseDir,
    )
    if outcome.isProblematic(): return icm.EH_badOutcome(outcome)    

    return( os.path.join(
        outcome.results, "unisos", "data"
    ))

####+BEGIN: bx:dblock:python:func :funcName "bpbBisosPkg_baseObtain_tmp" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisosPkg_baseObtain_tmp/ funcType=obtain retType=bool deco= argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbBisosPkg_baseObtain_tmp(
    baseDir,
):
####+END:
    outcome = bxpRootGet().cmnd(
        interactive=False,
        baseDir=baseDir,
    )
    if outcome.isProblematic(): return icm.EH_badOutcome(outcome)    

    return( os.path.join(
        outcome.results, "unisos", "data"
    ))

####+BEGIN: bx:dblock:python:func :funcName "bpbBisosPkg_baseObtain_log" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisosPkg_baseObtain_log/ funcType=obtain retType=bool deco= argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbBisosPkg_baseObtain_log(
    baseDir,
):
####+END:
    outcome = bxpRootGet().cmnd(
        interactive=False,
        baseDir=baseDir,
    )
    if outcome.isProblematic(): return icm.EH_badOutcome(outcome)    

    return( os.path.join(
        outcome.results, "unisos", "data"
    ))


####+BEGIN: bx:dblock:python:func :funcName "bpbBisosPkg_baseObtain_control" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisosPkg_baseObtain_control/ funcType=obtain retType=bool deco= argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbBisosPkg_baseObtain_control(
    baseDir,
):
####+END:
    outcome = bxpRootGet().cmnd(
        interactive=False,
        baseDir=baseDir,
    )
    if outcome.isProblematic(): return icm.EH_badOutcome(outcome)    

    return( os.path.join(
        outcome.results, "unisos", "data"
    ))



####+BEGIN: bx:dblock:python:func :funcName "bpbBisosPkg_baseObtain_input" :funcType "obtain" :retType "bool" :deco "" :argsList "baseDir"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bpbBisosPkg_baseObtain_input/ funcType=obtain retType=bool deco= argsList=(baseDir)  [[elisp:(org-cycle)][| ]]
"""
def bpbBisosPkg_baseObtain_input(
    baseDir,
):
####+END:
    outcome = bxpRootGet().cmnd(
        interactive=False,
        baseDir=baseDir,
    )
    if outcome.isProblematic(): return icm.EH_badOutcome(outcome)    

    return( os.path.join(
        outcome.results, "unisos", "data"
    ))


####+BEGIN: bx:dblock:python:section :title "Common Arguments Specification"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Arguments Specification*
"""
####+END:


####+BEGIN: bx:dblock:python:func :funcName "commonParamsSpecify" :funcType "ParSpec" :retType "" :deco "" :argsList "icmParams"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-ParSpec   :: /commonParamsSpecify/ retType= argsList=(icmParams)  [[elisp:(org-cycle)][| ]]
"""
def commonParamsSpecify(
    icmParams,
):
####+END:
    icmParams.parDictAdd(
        parName='baseDir',
        parDescription="Bx Platform Base Dir",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--baseDir',
    )

    icmParams.parDictAdd(
        parName='pbdName',
        parDescription="Platform BaseDirs Dict Name",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--pbdName',
    )

        
####+BEGIN: bx:dblock:python:section :title "Common Examples Sections"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Common Examples Sections*
"""
####+END:

####+BEGIN: bx:dblock:python:func :funcName "examples_bxPlatformBaseDirsCommon" :funcType "examples" :retType "none" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-examples  :: /examples_bxPlatformBaseDirsCommon/ retType=none argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def examples_bxPlatformBaseDirsCommon(
):
####+END:
    icm.cmndExampleMenuChapter('* =BxP BaseDir=  ByStar Platform Base Dirs')

    cmndName = "bxpRootGet" ; cmndArgs = "" ;
    cps = collections.OrderedDict()
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "bxpRootGet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['baseDir'] = '/tmp/bxBase'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    icm.ex_gExecMenuItem(execLine="""cat {}""".format(bxpRootBaseDirPtrUserFile_obtain()),)
    icm.ex_gExecMenuItem(execLine="""cat {}""".format(bxpRootBaseDirPtrSysFile_obtain()),)
    icm.ex_gExecMenuItem(execLine="""ls -l {}""".format(bxpRootBaseDirDefault_obtain(),))
    #icm.ex_gExecMenuItem(execLine="""sudo mkdir /bystar; sudo chown lsipusr:employee /bystar""")
    icm.ex_gExecMenuItem(execLine="""sudo mkdir /bisos; sudo chown lsipusr:employee /bisos""")
  

####+BEGIN: bx:dblock:python:func :funcName "examples_bxPlatformBaseDirs" :funcType "examples" :retType "none" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-examples  :: /examples_bxPlatformBaseDirs/ funcType=examples retType=none deco= argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def examples_bxPlatformBaseDirs(
):
####+END:
    """
** Auxiliary examples to be commonly used.
"""
    #examples_bxPlatformBaseDirsCommon()

    icm.cmndExampleMenuChapter('* =BxP BaseDir=  ByStar Platform Base Dirs Command')
    
    menuLine = """"""
    icm.cmndExampleMenuItem(menuLine, icmName="bx-bases", verbosity='none')    


####+BEGIN: bx:dblock:python:func :funcName "examples_bxPlatformBaseDirsFull" :funcType "examples" :retType "none" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-examples  :: /examples_bxPlatformBaseDirsFull/ funcType=examples retType=none deco= argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def examples_bxPlatformBaseDirsFull(
):
####+END:
    """
** Common examples.
"""
    bxRootBase = bxpRoot_baseObtain(None)

    examples_bxPlatformBaseDirsCommon()
    
    icm.cmndExampleMenuChapter('* =Module=  Overview (desc, usage, status)')    
   
    cmndName = "overview_bxpBaseDir" ; cmndArgs = "moduleDescription moduleUsage moduleStatus" ;
    cps = collections.OrderedDict()
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    

    icm.cmndExampleMenuChapter(' =BxP DirBases=  *pbdShow/pbdVerify/pbdUpdate*')    
    
    cmndName = "pbdShow" ; cmndArgs = "/ dist" ;
    cps = collections.OrderedDict() ; cps['baseDir'] = '/tmp/BISOS'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    
    cmndName = "pbdShow" ; cmndArgs = "/ dist" ;
    cps = collections.OrderedDict() ; cps['baseDir'] = '/tmp/BISOS' ; cps['pbdName'] = 'bxpRoot'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    
    cmndName = "pbdUpdate" ; cmndArgs = "all" ;
    cps = collections.OrderedDict()
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pbdVerify" ; cmndArgs = "all" ;
    cps = collections.OrderedDict()
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    

    cmndName = "pbdShow" ; cmndArgs = "bxRoot bxRoot/var bxRoot/bisos" ;
    cps = collections.OrderedDict() ; cps['baseDir'] = '/tmp/BISOS'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
   
    cmndName = "pbdVerify" ; cmndArgs = "bxRoot bxRoot/var bxRoot/bisos" ;
    cps = collections.OrderedDict() ; cps['baseDir'] = '/tmp/BISOS'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
     
    cmndName = "pbdUpdate" ; cmndArgs = "bxRoot bxRoot/var bxRoot/bisos" ;
    cps = collections.OrderedDict() ; cps['baseDir'] = '/tmp/BISOS'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    icm.cmndExampleMenuChapter(' =BxP DirBases=  *pbdShow/pbdVerify/pbdUpdate*')    

    cmndName = "pbdListUpdate" ; cmndArgs = "pbdList_bystar" ;
    cps = collections.OrderedDict() ; cps['baseDir'] = '/tmp/BISOS'
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    cmndName = "pbdListUpdate" ; cmndArgs = "pbdList_bystar" ;
    cps = collections.OrderedDict() ; cps['baseDir'] =  bxRootBase
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    
####+BEGIN: bx:dblock:python:section :title "Misc To Be Sorted Out"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Misc To Be Sorted Out*
"""
####+END:


    
####+BEGIN: bx:dblock:python:func :funcName "bxUserId_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-Obtain    :: /bxUserId_obtain/ retType=str argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def bxUserId_obtain(
):
####+END:
    """
** ByStar platform base directory specification. 
"""
    return "lsipusr"


####+BEGIN: bx:dblock:python:func :funcName "bxGroupId_obtain" :funcType "Obtain" :retType "str" :deco "" :argsList ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-Obtain    :: /bxGroupId_obtain/ retType=str argsList=nil  [[elisp:(org-cycle)][| ]]
"""
def bxGroupId_obtain(
):
####+END:
    """
** ByStar platform base directory specification. 
"""
    return "employee"


####+BEGIN: bx:dblock:python:section :title "Base Dirs Specifications"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Base Dirs Specifications*
"""
####+END:


####+BEGIN: bx:dblock:python:icmItem :itemType "List" :itemTitle "pbdList_bystar" :comment "=OBSOLETED="
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || List           :: pbdList_bystar ==OBSOLETED==  [[elisp:(org-cycle)][| ]]
"""
####+END:

pbdList_bystarObsoleted = [
    "/"
    "var",
    "control",
    "data",
    "tmp",
    "log",    
    "dist",
    "vcAuth",
    "vcAnon",
    "bisos",
    "bsip",
    "blee",    
]


####+BEGIN: bx:dblock:python:func :funcName "pbdDict_bisosRoot" :comment "pbd Dictionary" :funcType "Init" :retType "bxpRootBaseDirsDict" :argsList "baseDir" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-Init      :: /pbdDict_bisosRoot/ =pbd Dictionary= retType=bxpRootBaseDirsDict argsList=(baseDir) deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def pbdDict_bisosRoot(
    baseDir,
):
####+END:

    pbdDict = collections.OrderedDict()

    root = bxpRoot_baseObtain(baseDir)
    pbdDict['/'] = bxpObjGet_baseDir(root, '')

    
    def fullDestPathGet(dstPathRel):
        return( os.path.join(
            root, dstPathRel,
        ))

    def directory(pathRel):
        pbdDict[pathRel] = bxpObjGet_baseDir(root, pathRel)

    def symLink(dstPathRel, srcPath, srcPathType='internal'):
        pbdDict[dstPathRel] = bxpObjGet_symLink(root, dstPathRel, srcPath, srcPathType=srcPathType)

    def command(dstPathRel, createCmnd):
        pbdDict[dstPathRel] = BxpBaseDir_Command(
            destPathRoot=root,
            destPathRel=dstPathRel,
            createCommand=createCmnd,
        )
        
    directory('dist')
    directory('dist/pip')
    directory('dist/pip/bisos')
    directory('dist/pip/bisos/bin')
    directory('dist/pip/bisos/input')                
    directory('dist/pip/blee')
    directory('dist/pip/bsip')

    directory('venv')
    command(  'venv/py2-bisos-3',
              "virtualenv --no-site-packages --python=python2 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('venv/py2-bisos-3')))
    command(  'venv/dev-py2-bisos-3',
              "virtualenv --no-site-packages --python=python2 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('venv/dev-py2-bisos-3')))
    command(  'venv/py3-bisos-3',
              "virtualenv --no-site-packages --python=python3 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('venv/py3-bisos-3')))
    command(  'venv/dev-py3-bisos-3',
              "virtualenv --no-site-packages --python=python3 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('venv/dev-py3-bisos-3')))

    
    directory('vcAuth')
    directory('vcAuth/bisos')
    
    directory('vcAnon')
    directory('vcAnon/bisos')    

    directory('control')
    directory('control/bisos')    
    directory('control/bisos/site')    

    directory('var')
    directory('var/bisos')
    directory('var/bisos/icmsPkg')        
    
    
    directory('tmp')
    
    directory('log')
    directory('log/bisos')

    directory('core')
    symLink(  'core/bin', 'dist/pip/core/bin')
    symLink(  'core/input', 'dist/pip/core/input')
    symLink(  'core/var', 'var/core')
    symLink(  'core/tmp', 'tmp')
    symLink(  'core/log', 'log/core')                
              
    directory('bsip')
    
    directory('blee')

    return pbdDict




####+BEGIN: bx:dblock:python:func :funcName "pbdDict_bxpRootObsoleted" :comment "pbd Dictionary" :funcType "Init" :retType "bxpRootBaseDirsDict" :argsList "baseDir" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-Init      :: /pbdDict_bxpRootObsoleted/ =pbd Dictionary= retType=bxpRootBaseDirsDict argsList=(baseDir) deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def pbdDict_bxpRootObsoleted(
    baseDir,
):
####+END:

    pbdDict = collections.OrderedDict()

    root = bxpRoot_baseObtain(baseDir)
    pbdDict['/'] = bxpObjGet_baseDir(root, '')

    
    def fullDestPathGet(dstPathRel):
        return( os.path.join(
            root, dstPathRel,
        ))

    def directory(pathRel):
        pbdDict[pathRel] = bxpObjGet_baseDir(root, pathRel)

    def symLink(dstPathRel, srcPath, srcPathType='internal'):
        pbdDict[dstPathRel] = bxpObjGet_symLink(root, dstPathRel, srcPath, srcPathType=srcPathType)

    def command(dstPathRel, createCmnd):
        pbdDict[dstPathRel] = BxpBaseDir_Command(
            destPathRoot=root,
            destPathRel=dstPathRel,
            createCommand=createCmnd,
        )
        
    directory('dist')
    directory('dist/venv')
    command(  'dist/venv/py2-bisos-3',
              "virtualenv --no-site-packages --python=python2 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('dist/venv/py2-bisos-3')))
    command(  'dist/venv/dev-py2-bisos-3',
              "virtualenv --no-site-packages --python=python2 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('dist/venv/dev-py2-bisos-3')))
    command(  'dist/venv/py3-bisos-3',
              "virtualenv --no-site-packages --python=python3 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('dist/venv/py3-bisos-3')))
    command(  'dist/venv/dev-py3-bisos-3',
              "virtualenv --no-site-packages --python=python3 {fullDestPathGet}"
              .format(fullDestPathGet=fullDestPathGet('dist/venv/dev-py3-bisos-3')))
    directory('dist/pip')
    directory('dist/pip/bisos')
    directory('dist/pip/bisos/bin')
    directory('dist/pip/bisos/input')                
    directory('dist/pip/blee')
    directory('dist/pip/bsip')    
    
    directory('vcAuth')
    directory('vcAuth/bisos')
    
    directory('vcAnon')
    directory('vcAnon/bisos')    

    directory('control')
    directory('control/bisos')    
    directory('control/bisos/site')    

    directory('var')
    directory('var/bisos')
    directory('var/bisos/icmsPkg')        
    
    directory('tmp')
    
    directory('log')
    directory('log/bisos')

    directory('bisos')
    symLink(  'bisos/bin', 'dist/pip/bisos/bin')
    symLink(  'bisos/input', 'dist/pip/bisos/input')
    symLink(  'bisos/var', 'var/bisos')
    symLink(  'bisos/tmp', 'tmp')
    symLink(  'bisos/log', 'log/bisos')                
              
    directory('bsip')
    
    directory('blee')

    return pbdDict


####+BEGIN: bx:dblock:python:section :title "ICM Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ICM Commands*
"""
####+END:


####+BEGIN: bx:dblock:python:func :funcName "bxpRoot_baseObtain" :funcType "obtain" :retType "str" :argsList "baseDir" :deco "ucf.runOnceOnlyReturnFirstInvokation"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-obtain    :: /bxpRoot_baseObtain/ retType=str argsList=(baseDir) deco=ucf.runOnceOnlyReturnFirstInvokation  [[elisp:(org-cycle)][| ]]
"""
@ucf.runOnceOnlyReturnFirstInvokation
def bxpRoot_baseObtain(
    baseDir,
):
####+END:
    outcome = bxpRootGet().cmnd(
        interactive=False,
        baseDir=baseDir,
    )
    if outcome.isProblematic(): return icm.EH_badOutcome(outcome)    

    return outcome.results

    
####+BEGIN: bx:dblock:python:icm:cmnd:classHead :modPrefix "new" :cmndName "bxpRootGet" :parsMand "" :parsOpt "baseDir" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /bxpRootGet/ parsMand= parsOpt=baseDir argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class bxpRootGet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'baseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        baseDir=None,         # or Cmnd-Input
    ):
        #G = IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'baseDir': baseDir, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        baseDir = callParamsDict['baseDir']
####+END:
	def cmndDesc(): """
** if --baseDir Was specified, it is returned
** If ~/.bystarRoot exists, its content is returned
** If /etc/bystarRoot exists, its content is returned
** If /bystar exists, "/bystar" is returned
"""
        retVal = None
        while True:
            if baseDir:
                retVal = baseDir
                break

            userFileName = bxpRootBaseDirPtrUserFile_obtain()
            if os.path.isfile(
                    userFileName
            ):
                with open(userFileName, 'r') as myfile:
                    data=myfile.read().replace('\n', '')
                    retVal = data
                    break

            sysFileName = bxpRootBaseDirPtrSysFile_obtain()
            if os.path.isfile(
                    sysFileName
            ):
                with open(sysFileName, 'r') as myfile:
                    data=myfile.read().replace('\n', '')
                    retVal = data
                    break

            # Default ByStar Root Directory
            defaultBxRootDir = bxpRootBaseDirDefault_obtain()
            if os.path.isdir(defaultBxRootDir):
                retVal = defaultBxRootDir
                break

            icm.EH_problem_usageError("Missing /bystar and no /etc/bystarRoot")            
            retVal = None
            break

        if interactive:
            icm.ANN_write("{}".format(retVal))

        return cmndOutcome.set(
            opError=icm.notAsFailure(retVal),
            opResults=retVal,
        )


####+BEGIN: bx:dblock:python:subSection :title "ICM Each Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *ICM Each Commands*
"""
####+END:
            
            
####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "pbdShow" :parsMand "" :parsOpt "baseDir pbdName" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pbdShow/ parsMand= parsOpt=baseDir pbdName argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pbdShow(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'baseDir', 'pbdName', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        baseDir=None,         # or Cmnd-Input
        pbdName=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        G = icm.IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'baseDir': baseDir, 'pbdName': pbdName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        baseDir = callParamsDict['baseDir']
        pbdName = callParamsDict['pbdName']
####+END:
	def cmndDesc(): """
** for each arg, output bxp parameters.
"""
        icm.ANN_write("{}".format(baseDir))

        if not pbdName:
            pbdName = 'bxpRoot'

        if baseDir:
            pbdDict = eval("""pbdDict_{}("{}")""".format(pbdName, baseDir))
        else:
            pbdDict = eval("""pbdDict_{}({})""".format(pbdName, baseDir))

        def procEach(pbdItem):
            pbdObj = pbdDict[pbdItem]
            pbdObj.show()

        if effectiveArgsList[0] == "all":
            for each in pbdDict:
                procEach(each)

            return cmndOutcome.set(
                opError=icm.OpError.Success,
                opResults=None,
            )
 
        for each in  effectiveArgsList:
            procEach(each)
            
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )
    
####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "pbdVerify" :parsMand "" :parsOpt "baseDir pbdName" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pbdVerify/ parsMand= parsOpt=baseDir pbdName argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pbdVerify(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'baseDir', 'pbdName', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        baseDir=None,         # or Cmnd-Input
        pbdName=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        G = icm.IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'baseDir': baseDir, 'pbdName': pbdName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        baseDir = callParamsDict['baseDir']
        pbdName = callParamsDict['pbdName']
####+END:
	def cmndDesc(): """
** for each arg, verify that each exists as expected.
"""
        icm.ANN_write("{}".format(baseDir))
                
        if not pbdName:
            pbdName = 'bxpRoot'

        if baseDir:
            pbdDict = eval("""pbdDict_{}("{}")""".format(pbdName, baseDir))
        else:
            pbdDict = eval("""pbdDict_{}({})""".format(pbdName, baseDir))

        def procEach(pbdItem):
            pbdObj = pbdDict[pbdItem]
            pbdObj.verify()

        if effectiveArgsList[0] == "all":
            for each in pbdDict:
                procEach(each)

            return cmndOutcome.set(
                opError=icm.OpError.Success,
                opResults=None,
            )
 
        for each in  effectiveArgsList:
            procEach(each)
            
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )
 
####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "pbdUpdate" :parsMand "" :parsOpt "baseDir pbdName" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pbdUpdate/ parsMand= parsOpt=baseDir pbdName argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pbdUpdate(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'baseDir', 'pbdName', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        baseDir=None,         # or Cmnd-Input
        pbdName=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        G = icm.IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'baseDir': baseDir, 'pbdName': pbdName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        baseDir = callParamsDict['baseDir']
        pbdName = callParamsDict['pbdName']
####+END:
	def cmndDesc(): """
** For each arg, update each to what has been specified.
"""
        icm.ANN_write("{}".format(baseDir))
                
        if not pbdName:
            #pbdName = 'bxpRoot'
            pbdName = 'bisosRoot'

        if baseDir:
            pbdDict = eval("""pbdDict_{}("{}")""".format(pbdName, baseDir))
        else:
            pbdDict = eval("""pbdDict_{}({})""".format(pbdName, baseDir))

        def procEach(pbdItem):
            pbdObj = pbdDict[pbdItem]
            pbdObj.update()

        if effectiveArgsList[0] == "all":
            for each in pbdDict:
                procEach(each)

            return cmndOutcome.set(
                opError=icm.OpError.Success,
                opResults=None,
            )
 
        for each in  effectiveArgsList:
            procEach(each)
            
        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )
 

        
####+BEGIN: bx:dblock:python:subSection :title "ICM List Commands"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *ICM List Commands*
"""
####+END:
    

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :cmndName "pbdListUpdate" :parsMand "" :parsOpt "baseDir pbdName" :argsMin "1" :argsMax "1000" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pbdListUpdate/ parsMand= parsOpt=baseDir pbdName argsMin=1 argsMax=1000 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pbdListUpdate(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'baseDir', 'pbdName', ]
    cmndArgsLen = {'Min': 1, 'Max': 1000,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        baseDir=None,         # or Cmnd-Input
        pbdName=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        G = icm.IcmGlobalContext()
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'baseDir': baseDir, 'pbdName': pbdName, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        baseDir = callParamsDict['baseDir']
        pbdName = callParamsDict['pbdName']
####+END:
	def cmndDesc(): """
** Doc String Outside Of Dblock.
"""
        icm.ANN_write("{}".format(baseDir))

        for eachArg in  effectiveArgsList:
            pbdList = eval('{}'.format(eachArg))
            for each in pbdList:
                pbdUpdate().cmnd(
                    interactive=False,
                    baseDir=baseDir,
                    argsList=each.split(),
                )

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )


####+BEGIN: bx:dblock:python:section :title "BxpBaseDir Classes"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *BxpBaseDir Classes*
"""
####+END:
    

####+BEGINNOT: bx:dblock:python:enum :enumName "bpd_BaseDirType" :comment ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Enum           :: /bpd_BaseDirType/  [[elisp:(org-cycle)][| ]]
"""
#@enum.unique
class bpd_BaseDirType(enum.Enum):
####+END:
    directory = 'directory'
    symLink = 'symLink'
    gitClone = 'gitClone'


####+BEGIN: bx:dblock:python:func :funcName "bxpObjGet_baseDir" :funcType "BxPD" :retType "BxpBaseDir_Dir" :argsList "pathRoot pathRel" :deco "default"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-BxPD      :: /bxpObjGet_baseDir/ retType=BxpBaseDir_Dir argsList=(pathRoot pathRel) deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def bxpObjGet_baseDir(
    pathRoot,
    pathRel,
):
####+END:
    return (
        BxpBaseDir_Dir(
            destPathRoot=pathRoot,
            destPathRel=pathRel,
        )
    )

####+BEGIN: bx:dblock:python:func :funcName "bxpObjGet_symLink" :comment "Incomplete" :funcType "BxPD" :retType "BxpBaseDir_SymLink" :argsList "pathRoot dstPathRel srcPath srcPathType='internal'" :deco "default"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-BxPD      :: /bxpObjGet_symLink/ =Incomplete= retType=BxpBaseDir_SymLink argsList=(pathRoot dstPathRel srcPath srcPathType='internal') deco=default  [[elisp:(org-cycle)][| ]]
"""
@icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
def bxpObjGet_symLink(
    pathRoot,
    destPathRel,
    srcPath,
    srcPathType='internal',
):
####+END:
    return (
        BxpBaseDir_SymLink(
            destPathRoot=pathRoot,
            destPathRel=destPathRel,
            srcPath=srcPath,
            srcPathType=srcPathType,
        )
    )




####+BEGIN: bx:dblock:python:subSection :title "Class Definitions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Class Definitions*
"""
####+END:



####+BEGIN: bx:dblock:python:class :className "BxpBaseDir" :superClass "object" :comment "Expected to be subclassed" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /BxpBaseDir/ object =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class BxpBaseDir(object):
####+END:
    """	
** ByStar platform base directory specification. 	
"""
    owner = bxUserId_obtain()
    group = bxGroupId_obtain()
    permissions = "775"
    
    def __init__(
        self,
        baseDirType=None,
        destPathRoot=None,
        destPathRel=None,            
    ):
        self.baseDirType=baseDirType
        self.destPathRoot=destPathRoot
        self.destPathRel=destPathRel

    def destPathFullGet(self,):
        return (
            os.path.abspath(
                os.path.join(self.destPathRoot, self.destPathRel)
            )
        )
        


####+BEGIN: bx:dblock:python:class :className "BxpBaseDir_Dir" :superClass "BxpBaseDir" :comment "Actual" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /BxpBaseDir_Dir/ BxpBaseDir =Actual=  [[elisp:(org-cycle)][| ]]
"""
class BxpBaseDir_Dir(BxpBaseDir):
####+END:
    """	
** ByStar platform base directory specification. 	
"""
    
    def __init__(
        self,
        baseDirType=bpd_BaseDirType.directory,
        destPathRoot=None,
        destPathRel=None,            
        basePrepFunc=None,
        baseCleanFunc=None,
        comment=None,                        
    ):
        self.baseDirType=baseDirType
        self.destPathRoot=destPathRoot
        self.destPathRel=destPathRel
        self.basePrepFunc=basePrepFunc
        self.baseCleanFunc=baseCleanFunc
        self.comment=comment

    def __str__(self):
        return (
            """
baseDirType={baseDirType}
destPathRoot={destPathRoot}
destPathRel={destPathRel}
owner={owner}
group={group}
permissions={permissions}
basePrepFunc={basePrepFunc}
baseCleanFunc={baseCleanFunc}
comment={comment}
""".format(
    baseDirType=self.baseDirType,
    destPathRoot=self.destPathRoot,
    destPathRel=self.destPathRel,
    owner=self.__class__.owner,
    group=self.__class__.group,
    permissions=self.__class__.permissions,
    basePrepFunc=self.basePrepFunc,
    baseCleanFunc=self.baseCleanFunc,
    comment=self.comment,
        ))

    def update(self):
        destFullPath = self.destPathFullGet()
        if os.path.isdir(destFullPath):
            icm.ANN_here("{} Exists -- mkdir Skipped".format(destFullPath))
        else:
            try:
                os.makedirs(destFullPath)
            except OSError:
                if not os.path.isdir(destFullPath):
                    raise
            icm.ANN_write("Created {}".format(destFullPath))


    def verify(self):
        destFullPath = self.destPathFullGet()        
        if os.path.isdir(destFullPath):
            icm.ANN_here("{} Exists -- As Expected".format(destFullPath))
        else:
            icm.ANN_here("{} Missing -- Un-Expected".format(destFullPath))
        
    def show(self):
        icm.ANN_write("{}".format(self.__str__()))
        
    


####+BEGIN: bx:dblock:python:class :className "BxpBaseDir_SymLink" :superClass "BxpBaseDir" :comment "Actual" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /BxpBaseDir_SymLink/ BxpBaseDir =Actual=  [[elisp:(org-cycle)][| ]]
"""
class BxpBaseDir_SymLink(BxpBaseDir):
####+END:
    """	
** ByStar platform base directory specification. 	
"""
    
    def __init__(
        self,
        destPathRoot,
        destPathRel,
        srcPath,
        srcPathType='internal',            
        basePrepFunc=None,
        baseCleanFunc=None,
        comment=None,                        
    ):
        self.baseDirType=bpd_BaseDirType.symLink
        self.destPathRoot=destPathRoot
        self.destPathRel=destPathRel
        self.srcPath=srcPath
        self.srcPathType=srcPathType        
        self.basePrepFunc=basePrepFunc
        self.baseCleanFunc=baseCleanFunc
        self.comment=comment

    def __str__(self):
        return (
            """
baseDirType={baseDirType}
destPathRoot={destPathRoot}
srcPath={srcPath}
srcPathType={srcPathType}
owner={owner}
group={group}
permissions={permissions}
basePrepFunc={basePrepFunc}
baseCleanFunc={baseCleanFunc}
comment={comment}
""".format(
    baseDirType=self.baseDirType,
    destPathRoot=self.destPathRoot,
    srcPath=self.srcPath,
    srcPathType=self.srcPathType,
    destPathRel=self.destPathRel,    
    owner=self.__class__.owner,
    group=self.__class__.group,
    permissions=self.__class__.permissions,
    basePrepFunc=self.basePrepFunc,
    baseCleanFunc=self.baseCleanFunc,
    comment=self.comment,
        ))

    def srcFullPathObtain(self):
        # NOTYET, check srcPathType
        return (
            os.path.abspath(
                os.path.join(self.destPathRoot, self.srcPath)
            )
        )
    

    def update(self):
        destFullPath = self.destPathFullGet()
        srcFullPath = self.srcFullPathObtain()

        def createSymLink():
            try:            
                os.remove(destFullPath)
            except OSError:
                pass
            
            try:
                os.symlink(srcFullPath, destFullPath)
            except OSError:
                if not os.path.islink(destFullPath):
                    raise
            icm.ANN_write("Created {} SymLink pointing to: {}".format(
                destFullPath, srcFullPath))
        
        if os.path.islink(destFullPath):
            linkPointsToPath = os.readlink(destFullPath)
            if srcFullPath == linkPointsToPath:
                icm.ANN_here("{} SymLink exists and correctly points to: {}".format(
                    destFullPath, srcFullPath))
            else:
                createSymLink() 
        else:
            createSymLink()


    def verify(self):
        destFullPath = self.destPathFullGet()
        srcFullPath = self.srcFullPathObtain()

        if os.path.islink(destFullPath):
            linkPointsToPath = os.readlink(destFullPath)
            if srcFullPath == linkPointsToPath:
                icm.ANN_here("{} SymLink exists and correctly points to: {}".format(
                    destFullPath, srcFullPath))
            else:
                icm.ANN_here("{} SymLink exists but is wrong -- points to: {} instead of".format(
                    destFullPath, linkPointsToPath, srcFullPath))
        else:
            icm.ANN_here("{} SymLink is missing".format(
                destFullPath,))

        
    def show(self):
        icm.ANN_write("{}".format(self.__str__()))
        



####+BEGIN: bx:dblock:python:class :className "BxpBaseDir_Command" :superClass "BxpBaseDir" :comment "Actual" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /BxpBaseDir_Command/ BxpBaseDir =Actual=  [[elisp:(org-cycle)][| ]]
"""
class BxpBaseDir_Command(BxpBaseDir):
####+END:
    """	
** ByStar platform base directory specification. 	
"""
    
    def __init__(
        self,
        destPathRoot,
        destPathRel,
        createCommand,
        basePrepFunc=None,
        baseCleanFunc=None,
        comment=None,                        
    ):
        self.baseDirType=bpd_BaseDirType.symLink
        self.destPathRoot=destPathRoot
        self.destPathRel=destPathRel
        self.createCommand=createCommand
        self.basePrepFunc=basePrepFunc
        self.baseCleanFunc=baseCleanFunc
        self.comment=comment

    def __str__(self):
        return (
            """
baseDirType={baseDirType}
destPathRoot={destPathRoot}
createCommand={createCommand}
owner={owner}
group={group}
permissions={permissions}
basePrepFunc={basePrepFunc}
baseCleanFunc={baseCleanFunc}
comment={comment}
""".format(
    baseDirType=self.baseDirType,
    destPathRoot=self.destPathRoot,
    createCommand=self.createCommand,
    destPathRel=self.destPathRel,    
    owner=self.__class__.owner,
    group=self.__class__.group,
    permissions=self.__class__.permissions,
    basePrepFunc=self.basePrepFunc,
    baseCleanFunc=self.baseCleanFunc,
    comment=self.comment,
        ))


    def update(self):
        destFullPath = self.destPathFullGet()
        if os.path.isdir(destFullPath):
            icm.ANN_here("{} Exists -- mkdir Skipped".format(destFullPath))
            return None

        outcome = icm.subProc_bash(
            self.createCommand,
        ).out()
        if outcome.isProblematic(): return icm.EH_badOutcome(outcome)
        

    def verify(self):            
        destFullPath = self.destPathFullGet()        
        if os.path.isdir(destFullPath):
            icm.ANN_here("{} Exists -- As Expected".format(destFullPath))
        else:
            icm.ANN_here("{} Missing -- Un-Expected".format(destFullPath))
            
        
    def show(self):
        icm.ANN_write("{}".format(self.__str__()))
        
        


####+BEGIN: bx:dblock:python:class :className "BxpBaseDir_GitClone" :superClass "BxpBaseDir" :comment "" :classType ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-         :: /BxpBaseDir_GitClone/ BxpBaseDir  [[elisp:(org-cycle)][| ]]
"""
class BxpBaseDir_GitClone(BxpBaseDir):
####+END:
    """	
** ByStar platform base directory specification. 	
"""
   
    def __init__(
        self,
        destPathRel=None,
    ):
        #self.baseDirType = 
        #self.__class__.destPathRel = destPathRel
        pass

    def __str__(self):
        return format(
            'baseDirType: ' + str(self.baseDirType)
        )
    

####+BEGIN: bx:dblock:python:section :title "Slice Definitions PipPkgsList Classes"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Slice Definitions PipPkgsList Classes*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:
    


####+BEGIN: bx:dblock:python:subSection :title "Class Definitions"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ================ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]          *Class Definitions*
"""
####+END:



####+BEGIN: bx:dblock:python:class :className "PipPkgsList" :superClass "object" :comment "Expected to be subclassed" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /PipPkgsList/ object =Expected to be subclassed=  [[elisp:(org-cycle)][| ]]
"""
class PipPkgsList(object):
####+END:
    """	
** Process a pipPkgsList, which could be passed as inPkgsList or over-writen in pkgsListSpec.	
"""
   
    def __init__(
        self,
        virtualenvBaseDir,
        inPkgsList=None,
        pyVersion=None,
        bisosVersion=None,
    ):
        self.virtualenvBaseDir = virtualenvBaseDir        
        self.inPkgsList = inPkgsList
        self.pyVersion = pyVersion
        self.bisosVersion = bisosVersion
 
    def pkgsListSpec(self):
        pl = collections.OrderedDict()
        pl['pkgName'] = "cur"  # pkgVersion
        return pl

    def pkgsListObtain(self):
        if self.inPkgsList:
            return self.inPkgsList
        else:
            return self.pkgsListSpec()
    
    def __str__(self):
        pkgsList = self.pkgsListObtain()        
        return (
            """NOTYET,  {}""".format(pkgsList)
        )

    def execActionStr(self, actionStr):
        if actionStr == "verify":
            return self.verify()
        elif actionStr == "show":
            return self.show()
        elif actionStr == "update":
            return self.update()
        elif actionStr == "list":
            return self.list()
        else:
            icm.EH_critical_oops("")
            return

    def list(self):
        pkgsList = self.pkgsListObtain()
        for each in pkgsList:
            icm.ANN_write(each)
        return pkgsList
 
    def verify(self):
        pkgsList = self.pkgsListObtain()
        return pkgsList
        
    def show(self):
        icm.ANN_write("{}".format(self.__str__()))
        
    def update(self):
        pkgsList = self.pkgsListObtain()
        activateFile = os.path.join(self.virtualenvBaseDir, "bin/activate")
        for each in pkgsList:
            outcome = icm.subProc_bash(
                """\
source {activateFile}; \
pip install --no-cache-dir {each}; \
"""
                .format(activateFile=activateFile, each=each)
            ).out()
            if outcome.isProblematic(): return icm.EH_badOutcome(outcome)



####+BEGIN: bx:dblock:python:class :className "PipPkgsList_BisosFoundation" :superClass "PipPkgsList" :comment "Actual" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /PipPkgsList_BisosFoundation/ PipPkgsList =Actual=  [[elisp:(org-cycle)][| ]]
"""
class PipPkgsList_BisosFoundation(PipPkgsList):
####+END:
    """	
** SubClassed with pkgsListSpec	
"""
 
    def pkgsListSpec(self):
        pl = collections.OrderedDict()
        pl['coverage'] = "cur"
        return pl

            

####+BEGIN: bx:dblock:python:class :className "PipPkgsList_BisosBase" :superClass "PipPkgsList" :comment "Actual" :classType "basic"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-basic    :: /PipPkgsList_BisosBase/ PipPkgsList =Actual=  [[elisp:(org-cycle)][| ]]
"""
class PipPkgsList_BisosBase(PipPkgsList):
####+END:
    """	
** SubClassed with pkgsListSpec	
"""
 
    def pkgsListSpec(self):
        pl = collections.OrderedDict()
        pl['unisos'] = "cur"
        pl['unisos.ucf'] = "cur"
        pl['unisos.icm'] = "cur"
        pl['unisos.common'] = "cur"
        pl['unisos.x822Msg'] = "cur"
        pl['unisos.marme'] = "cur"
        
        pl['bisos'] = "cur"
        pl['bisos.common'] = "cur"
        pl['bisos.bx-bases'] = "cur"
        pl['bisos.things'] = "cur"
        pl['bisos.gossonot'] = "cur"        
        return pl

            
    

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
