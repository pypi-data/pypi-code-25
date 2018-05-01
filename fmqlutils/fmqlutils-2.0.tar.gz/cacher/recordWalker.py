import os
import re
import json
from collections import defaultdict, OrderedDict
from datetime import datetime

"""
Utils for on-disk (vs in Mongo) clone data and meta data analysis.

TODO:
- support walking through data slices (ex/ subset of docs by type)
"""

DATASET_BASE = "/data/"
    
class ResourceTypeWalker:

    def __init__(self, systemId, resourceType, ordered=False, njsnDirName=""):
        self.__systemId = systemId
        self.__resourceType = resourceType
        self.__ordered = False # much slower if ordered
        self.__njsnDirName = njsnDirName if njsnDirName else "NJSN"
        
    def __iter__(self):
        for resource in self.walk():
            yield resource

    def walk(self, resourceFilter=None):
        locn = DATASET_BASE + self.__systemId + "/" + self.__njsnDirName + "/"
        for f in os.listdir(locn):
            if not re.match(self.__resourceType + "[\.\-]", f):
                continue
            if self.__ordered: # much slower
                contents = json.load(open(locn + f), object_pairs_hook=OrderedDict)
            else:
                contents = json.load(open(locn + f))
            if not isinstance(contents, list):
                if not (isinstance(contents, dict) and "@graph" in contents):
                    raise Exception("If not just list of data, expected context/graph combo in NJSN")
                contents = contents["@graph"]
            for resource in contents:
                if resourceFilter and not resourceFilter.filter(resource):
                    continue
                yield resource

class ResourceSubTypeFilter:

    def __init__(self, fmType=""):
        self.__fmType = fmType # allows you to avoid suffix of type
        self.__propertyValueRestrictions = {}
        self.__hasOneOfProperties = None
        self.__hasAllOfProperties = None
        self.__hasNoneOfProperties = None
        self.__filterFuncs = None

    def __str__(self):
        mu = ""
        if len(self.__propertyValueRestrictions):
            mu += "(" + " & ".join((p.split("-")[0] + "=" + str(v)) for p, v in self.__propertyValueRestrictions.iteritems()) + ")"
        def addMUPropSet(label, st, separate):
            smu = ""
            if not st: 
                return ""
            if separate:
                smu += " & " 
            smu += label + "(" + ", ".join(p.split("-")[0] for p in st) + ")"
            return smu
        mu += addMUPropSet("oneOf", self.__hasOneOfProperties, (mu != ""))
        mu += addMUPropSet("allOf", self.__hasAllOfProperties, (mu != ""))
        mu += addMUPropSet("noneOf", self.__hasNoneOfProperties, (mu != ""))
        if self.__filterFuncs:
            if mu:
                mu += " & " 
            mu += " & ".join("filter(" + ffInfo["descr"] + ")" for ffInfo in self.__filterFuncs)
        return mu

    def __suffixProperty(self, property):
        if not re.search(r'\-', property):
            return property + "-" + self.__fmType
        if not re.search(self.__fmType + "$", property):
            raise Exception("Property <" + property + "> must end in fmType " + self.__fmType)
        return property

    def restrictPropertyValue(self, property, value):
        self.__propertyValueRestrictions[self.__suffixProperty(property)] = value

    def hasOneOfProperties(self, properties):
        self.__hasOneOfProperties = set(self.__suffixProperty(property) for property in properties)

    def hasNoneOfProperties(self, properties):
        self.__hasNoneOfProperties = set(self.__suffixProperty(property) for property in properties)

    def hasAllOfProperties(self, properties):
        self.__hasAllOfProperties = set(self.__suffixProperty(property) for property in properties)

    def setFilterFuncs(self, ffInfos): # takes resource
        self.__filterFuncs = ffInfos

    def filter(self, resource):
        for property, value in self.__propertyValueRestrictions.iteritems():
            if property not in resource:
                return False
            if resource[property] != value:
                return False
        if self.__hasOneOfProperties and len(self.__hasOneOfProperties & set(resource.keys())) == 0:
            return False
        if self.__hasNoneOfProperties and len(self.__hasNoneOfProperties & set(resource.keys())) != 0:
            return False # EIE stuff
        if self.__hasAllOfProperties and not self.__hasAllOfProperties.issubset(set(resource.keys())):
            return False
        if self.__filterFuncs:
            for ffInfo in self.__filterFuncs:
                if not ffInfo["func"](resource):
                    return False
        return True

class ResourceSubTypeGrouper:
    """
    Groupers use the values of particular properties (which may be
    absent) to assign a resource to a group.

    Use in combination with defaultdict as iterate resources.
    """
    def __init__(self, fmType):
        pass

"""
VISTA dates 'spread' as always using $NOW so exact === won't catch <=> dates.
"""
def dateDiffOverThreshold(dt1, dt2, threshold):
    try:
        dtDiff = datetime.strptime(dt2, "%Y-%m-%dT%H:%M:%S") - datetime.strptime(dt1, "%Y-%m-%dT%H:%M:%S")
    except:
        print "can't diff", dt1, dt2
        return True
    if dtDiff.total_seconds() > threshold:
        return True
    return False

# ######################## TEST ######################

def main():

    rtw = ResourceTypeWalker("LOCALVISTA", "120_8")

    total = sum(1 for resource in rtw)
 
    print "Total Allergy (120_8)", total

    rstf = ResourceSubTypeFilter("120_8")
    rstf.restrictPropertyValue("observed_historical", "OBSERVED")
    print rstf, sum(1 for resource in rtw.walk(rstf))
    print 
    print


if __name__ == "__main__":
    main()
