#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import json
from datetime import datetime
import re
from collections import defaultdict, OrderedDict
from shutil import copy2
import random

"""
TODO: must mix/merge with ResourceWalker in Cacher ... (may rename to Cache)
"""
class FMQLReplyIterator:

    def __init__(self, dmDir, onlyTypes=None, excludeTypesFilter=None):
        self.__dmDir = dmDir
        self.__flsByTyp = defaultdict(list)
        # accepts both 200 and NEW PERSON-200
        onlyFMTypes = None
        if onlyTypes:
            onlyFMTypes = set([typ.split("-")[1] if re.search(r'\-', typ) else typ for typ in onlyTypes])
        for fl in os.listdir(dmDir):
            if not re.search(r'\.json$', fl):
                continue
            flTyp = fl.split("-")[0]
            if onlyFMTypes and flTyp not in onlyFMTypes:
                continue
            if excludeTypesFilter and excludeTypesFilter(flTyp):
                continue
            self.__flsByTyp[flTyp].append(fl)
        self.__currentFMQLReplyFile = ""

    def next(self):

        for typ in sorted(self.__flsByTyp, key=lambda x: float(re.sub("_", ".", x))):

            for fl in sorted(self.__flsByTyp[typ], key=lambda x: int(x.split("-")[1].split(".")[0])):

                self.__currentFMQLReplyFile = fl

                flJSON = json.load(open(self.__dmDir + "/" + fl), object_pairs_hook=OrderedDict)

                # Flexible for flat (ie/ just []) or reply form
                if not isinstance(flJSON, list):
                    flJSON = flJSON["results"]

                if len(flJSON) == 0:
                    continue

                for record in flJSON:
                    yield record

    def currentFMQLReplyFile(self):
        return self.__currentFMQLReplyFile

"""
Pass in schema definition and get (in json) a definition of location-based groupings

Note (from PATIENT-2) - some relevant ...

	.11
		street_address_line_1
		zip4
		street_address_line_2
		street_address_line_3
		city
		state
		zip_code
		county
		province
		postal_code
		country
		address_change_dt_tm
		address_change_source
		address_change_site
		bad_address_indicator
		address_change_user

        20
                date_esig_last_changed
                signature_block_printed_name
                signature_block_title
                electronic_signature_code

Some not ...

	NAME
		name_components
		kname_components
		k2name_components
		fathers_name_components
		mothers_name_components
		mothers_maiden_name_components
		ename_components
		e2name_components
		dname_components

"""
def groupPropertiesByLocation(schemaInfo):
    byLoc = defaultdict(list)
    for propInfo in schemaInfo["properties"]:
        fmLocation = propInfo["fmLocation"]
        fmLocFirst = fmLocation.split(";")[0]
        if fmLocFirst == "" or fmLocFirst == "0": # 0; are of all sorts
            continue
        byLoc[fmLocFirst].append(propInfo)
    # cull if not > 1
    byLoc = dict((loc, byLoc[loc]) for loc in byLoc if len(byLoc[loc]) > 1)
    return byLoc

"""
Fits with schema form needed for FMQL (vs one passed now)
"""
def generateVDMSummary(systemName, systemStationNumber):

    reducedDefns = []
    mpropsByChildId = {}
    schemaLocn = "/data/{}/JSON/".format(systemName)
    for sfl in os.listdir(schemaLocn):
        if not re.match(r'SCHEMA', sfl):
            continue
        schemaJSON = json.load(open(schemaLocn + sfl))
        info = {"id": schemaJSON["number"], "label": schemaJSON["name"]}
        if "parent" in schemaJSON:
            info["parent"] = schemaJSON["parent"]
            if len(schemaJSON["fields"]) == 1:
                info["isSingleton"] = True
        if "description" in schemaJSON:
            info["description"] = schemaJSON["description"]["value"]
        for fieldInfo in schemaJSON["fields"]:
            if fieldInfo["type"] == "9":
                mpropsByChildId[fieldInfo["details"]] = fieldInfo["pred"]
        reducedDefns.append(info)

    reducedDefnsById = dict((info["id"], info) for info in reducedDefns)

    # tops will get one or more child singleton paths (rem: no multiple types
    # in JSON
    for info in reducedDefns:
        if "parent" in info and "isSingleton" in info:
            pinfo = info
            path = []
            while True:
                if "parent" not in pinfo:
                    break
                path.insert(0, mpropsByChildId[pinfo["id"]])
                pinfo = reducedDefnsById[pinfo["parent"]]
            if "singletonPaths" not in pinfo:
                pinfo["singletonPaths"] = []
            pinfo["singletonPaths"].append("/".join(path))

    json.dump(reducedDefns, open("defnsCache/vdmSummary{}.json".format(systemStationNumber), "w"))
