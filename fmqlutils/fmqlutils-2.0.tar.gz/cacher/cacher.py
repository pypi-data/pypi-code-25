#!/usr/bin/env python

import os
import re 
import sys
import json
import shutil
from datetime import datetime
from collections import OrderedDict
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
from ..fmqlIF.fmqlIF import FMQLRESTIF, FMQLBrokerIF

"""
Basic FileMan data and schema cacher using FMQL. For any FM system (VISTA or CHCS)

Background: FileMan doesn't have enough indexes to support analytics. To fully analyze
data must first be cached. It can then be processed in a different DB (ex/ Mongo) or just
from disk.

Works off "/data/cacher/configs/" - default cache to "/data/vista/{vistaId}/DataV1/" which
it will create if it is absent

To test:
- du -h /data/{SYSTEM}/Data[V2] and /Schema
- old 2 download has 'File 2, limit 500 : all 1032150 of file 2 in 4:49:22.820342'

Invoke: 

    > nohup python -u cacher.py VISTACONFIG > nohupVISTA.out & and tail -f nohupVISTA.out; monitor with ps -aux, kill with kill -9 {pid}

or 'python cacher.py nodeVISTA SCHEMA'

------------------------------------------------------------

TODO:
1. Break out Exception - LOG error
2. Calc LIMIT for efficiency (say 1 minute bites) AND 
    to avoid CSP timeout
    - if timeout, /5 and go again (if get 503 explicitly ie/ catch it)
    - run through looking at timing - get around 15 seconds?
    - fits in with CSP failure/retry
    - also try calculate schema complexity and see if corresponds to limit problems ie/
      # of multiples (may not be good indication as don't know singleton vs many)
    NOTE: don't treat 503 the same as "connection timed out" which has happened when outside connections went down.
   ex INFO - Sending query number 2 after 5000 cached - DESCRIBE 80 LIMIT 5000 AFTERIEN 5000 CSTOP 6000
INFO - Queried and flushed 80 afterien 5000 in 0:06:37.622588 with 5000 resources ... far tooo long
3. Dataset management notions with Zipping with Meta being done as part of the process
4. move over to more formal option parsing with help etc
"""

# ########################## Data #########################

def cacheData(config):
    
    logging.info("Caching data of FM System {}".format(config["name"]))
    
    start = datetime.now()
        
    cacheLocation, dataCacheLocation, schemaCacheLocation, cacherLogLocation = ensureCacheLocation(config)

    configLogging(cacherLogLocation, config["logLevel"] if "logLevel" in config else "DEBUG")
    logging.info("caching in {}".format(cacheLocation))

    fmqlIF = makeFMQLIF(config)

    try:
        zeroFiles = json.load(open("{}trackZeroFiles{}.json".format(cacherLogLocation, config["name"])))
    except: 
        zeroFiles = []
        
    excludeTypes = set(config["excluded"]) if "excluded" in config else set()
    includeTypes = set(config["included"]) if "included" in config else None

    def files(fmqlEP, schemaCacheLocation, allFiles=False):
        """
        From SELECT TYPES - if in cache just load and read. Otherwise cache and
        then load and read.
        """
        query = "SELECT TYPES TOPONLY" # doing TOPONLY and not POPONLY in case POP is wrong
        cacheFile = re.sub(r' ', "_", query) + ".json"
        try:
            reply = json.load(open(schemaCacheLocation + cacheFile), object_pairs_hook=OrderedDict)
        except Exception:
            logging.info("First time through - must (re)cache {} to {} ...".format(query, schemaCacheLocation))
            reply = fmqlEP.invokeQuery(query)
            json.dump(reply, open(schemaCacheLocation + cacheFile, "w"))
        oresults = sorted(reply["results"], key=lambda res: int(res["count"]) if "count" in res else 0, reverse=True)
        filesInCountOrder = []
        for i, result in enumerate(oresults, 1):
            fileId = re.sub(r'\.', '_', result["number"])
            filesInCountOrder.append({"id": fileId, "count": 0 if "count" not in result else int(result["count"])})
        logging.info("Returning {} top files - not all will have data".format(len(filesInCountOrder)))
        return filesInCountOrder

    j = 0
    defaultLimit = 5000 if "defaultLimit" not in config else config["defaultLimit"]
    defaultCStop = 1000 if "defaultCStop" not in config else config["defaultCStop"]
    for i, fli in enumerate(files(fmqlIF, schemaCacheLocation, allFiles=False), 1):

        logging.info("{}. File {} expecting count of {} {}".format(i, fli["id"], fli["count"], "** Note POP says 0 but trying anyhow" if fli["count"] == 0 else ""))

        if fli["id"] in excludeTypes:
            logging.info("... but excluded explicitly so skipping")
            continue

        if fli["id"] in zeroFiles:
            logging.info("... but known to be empty ('zero file') so skipping")
            continue

        if includeTypes and fli["id"] not in includeTypes:
            logging.info("... skipping {} as not in explicit included list".format(fli["id"]))
            continue
            
        if "explicitLimits" in config and fli["id"] in config["explicitLimits"]:
            limit = config["explicitLimits"][fli["id"]]
        else:
            limit = defaultLimit

        if "explicitCStops" in config and fli["id"] in config["explicitCStops"]:
            cstop = config["explicitCStops"][fli["id"]]
        else:
            cstop = defaultCStop

        try: # may get license error - make sure save zero files first
            if not cacheFile(fmqlIF, dataCacheLocation, fli["id"], limit=limit, cstop=cstop, maxNumber=-1):
                zeroFiles.append(fli["id"])
        except:
            if len(zeroFiles):
                json.dump(zeroFiles, open("{}trackZeroFiles{}.json".format(cacherLogLocation, config["name"]), "w"))
            logging.info("End Caching due to ERROR")
            raise

    # Report result AND copy meta into 'about.json'
    about = config.copy()
    about["cacheEnd"] = datetime.now().strftime("%m/%d/%Y %I:%M%p")
    about["timeTaken"] = str(datetime.now() - start)
    if len(zeroFiles):
        about["zeroFiles"] = zeroFiles
    logging.info("Caching data done - took {}".format(about["timeTaken"]))
    json.dump(about, open(cacheLocation + "about.json", "w"), indent=4)
    json.dump(zeroFiles, open("{}trackZeroFiles{}.json".format(cacherLogLocation, config["name"]), "w"))
    
def cacheFile(fmqlIF, cacheLocation, fileType, limit=500, cstop=1000, maxNumber=-1):
    """
    File by file, cache data
    
    Mandatory arguments:
    - fmqlIF
    - cacheLocation: where to store the JSON
    - fileType: ex/ 2 or 120_5

    Optional/defaulted arguments:
    - limit for query: defaults to 1000
    - cstop for query: defaults to 10
    - filter for query: default is none
    - maxNumber: maximum number to retrieve. Default is no limit (-1)
    - afterIEN (for restart if necessary and for doing LIMIT at a time)
    - epWord: query used in CSP and node; Apache uses "fmql"
    """
    queryTempl = "DESCRIBE " + fileType + " LIMIT %(limit)s AFTERIEN %(afterien)s CSTOP " + str(cstop)

    # calculate afterien - last one already cached (can't know next) OR 0
    # ... allowing IEN of . (ex/ SYNTH CHCS 8461)
    afteriensSoFar = sorted([float(re.search(r'\-([\d\.]+)\.json$', f).group(1)) for f in os.listdir(cacheLocation) if os.path.isfile(os.path.join(cacheLocation, f)) and re.search('\.json$', f) and re.match(fileType + "\-", f)], reverse=True) 
    if len(afteriensSoFar) == 0:
        afterien = 0
    else:
        afterien = int(afteriensSoFar[0]) if afteriensSoFar[0].is_integer() else afteriensSoFar[0]
        lastReplyFile = cacheLocation + fileType + "-" + str(afterien) + ".json"
        lastReply = json.load(open(lastReplyFile)) 
        if "LIMIT" in lastReply["fmql"]:
            # REM: limit for next go may not be the same so not overriding limit
            lastLimit = int(lastReply["fmql"]["LIMIT"])
            if lastLimit > len(lastReply["results"]):
                logging.info("Got all of {} already - moving on".format(fileType))
                return True  
        lastResult = lastReply["results"][-1]
        lastId = lastResult["id"] if "id" in lastResult else lastResult["uri"]["value"]
        afterien = lastId.split("-")[1]
        logging.info("Still some of filetype {} left to get. Restarting with AFTERIEN {}".format(fileType, afterien))

    # queryNo and afterIEN are usually 0 but can start again    
    # Loop until there is no more or we reach the maximum
    numberOfTypeCached = 0
    start = datetime.now()
    queryNo = 0
    while True:
        queryNo += 1
        query = queryTempl % {"limit": limit, "afterien": afterien}
        logging.info("Sending query number {} after {} cached - {}".format(queryNo, numberOfTypeCached, query))
        queryStart = datetime.now()
        jreply = fmqlIF.invokeQuery(query)
        if "error" in jreply:
            logging.error("Received error reply: {}".format(jreply["error"]))
            raise Exception(jreply["error"])
        # Special case - first call (afterien=0) and no results => don't cache
        # ... REM: doing TOPONLY in case POPONLY is wrong. Means more queries but safer.
        # Ex for CHCS Synth: [u'3_081', u'66', u'52'] not in POP but have "data"
        # ... REM: afterien != 0 and no results then still cache as it means the case of
        # second to last LIMITED query filled up and then the last just returns none.
        # Note: alt is do a COUNT and then DESCRIBE if need be but largely the same cost.
        if afterien == 0 and len(jreply["results"]) == 0:
            logging.info("Empty {} - 0 replies afterien 0".format(fileType))
            return False 

        # V2 TBD: reconsider using full type name for dumped DM files
        jsonFileName = cacheLocation + fileType + "-" + str(afterien) + ".json"
        json.dump(jreply, open(jsonFileName, "w"))
        logging.info("Queried and flushed {} afterien {} in {} with {} resources".format(fileType, str(afterien), datetime.now() - queryStart, len(jreply["results"])))

        if len(jreply["results"]) == 0:
            break
        numberOfTypeCached += len(jreply["results"])
        if len(jreply["results"]) != int(limit):
            break
        # TODO: properly reset limit at the start to make sure maximum never exceeded
        if maxNumber != -1 and numberOfTypeCached >= maxNumber:
            logging.info("Breaking as got or exceeded maximum requested - {} - for {}".format(maxNumber, fileType))
            break
        lastResult = jreply["results"][-1]
        lastId = lastResult["id"] if "id" in lastResult else lastResult["uri"]["value"]
        afterien = lastId.split("-")[1]
        if (queryNo % 100) == 0:
            logging.debug("So far this has taken {}".format(datetime.now() - start))

    logging.info("Finished - cached {} - took {}".format(numberOfTypeCached, datetime.now() - start))

    return True
    
# ####################### Schema #####################
    
def cacheSchemas(config):
    """
    Other type of data - meta data
    """
    print
    print "Caching schema of FM System", config["name"]
    print
    
    start = datetime.now()
    
    cacheLocation, dataCacheLocation, schemaCacheLocation, cacherLogLocation = ensureCacheLocation(config)

    configLogging(cacherLogLocation, config["logLevel"] if "logLevel" in config else "DEBUG")

    fmqlIF = makeFMQLIF(config)
    
    query = "SELECT TYPES"
    try:
        jreply = json.load(open(schemaCacheLocation + "SELECT_TYPES.json"))
    except Exception:
        print "First time through - must (re)cache SELECT TYPES to", schemaCacheLocation, "..."
        jreply = fmqlIF.invokeQuery(query)
        json.dump(jreply, open(schemaCacheLocation + "SELECT_TYPES.json", "w"))

    # Not relying on OrderedDict
    fileIds = [re.sub(r'\.', "_", result["number"]) for result in jreply["results"]]
    alreadyCached = [re.match(r'SCHEMA\_([^\.]+)', f).group(1) for f in os.listdir(schemaCacheLocation) if os.path.isfile(os.path.join(schemaCacheLocation, f)) and re.search('\.json$', f) and re.match("SCHEMA_", f)]
    print "Must cache schema of", len(fileIds), "files ..."
    for fileId in fileIds:
        if fileId in alreadyCached:
            print "Got schema of", fileId, "already so going to next"
            continue
        print "Caching Schema of", fileId
        query = "DESCRIBE TYPE " + fileId
        queryStart = datetime.now()
        jreply = fmqlIF.invokeQuery(query)
        json.dump(jreply, open(schemaCacheLocation + "SCHEMA_" + fileId + ".json", "w"))

    # Phase 2 - cache SELECT TYPE REFS
    print "Must cache select type refs of", len(fileIds), "files ..."
    alreadyCached = [re.match(r'REFS\_([^\.]+)', f).group(1) for f in os.listdir(schemaCacheLocation) if os.path.isfile(os.path.join(schemaCacheLocation, f)) and re.search('\.json$', f) and re.match("REFS\_", f)]
    for fileId in fileIds:
        if fileId in alreadyCached:
            print "Got refs of", fileId, "already so going to next"
            continue
        print "Caching Refs of", fileId
        query = "SELECT TYPE REFS " + fileId
        queryStart = datetime.now()
        jreply = fmqlIF.invokeQuery(query)
        json.dump(jreply, open(schemaCacheLocation + "REFS_" + fileId + ".json", "w"))
        
    print 
    print "Schema (SELECT and REFs) caching took", datetime.now() - start, "for", len(fileIds), "files"
    print
    
# #################### Setups for Caching #######################
    
"""
/{baseLocation}|data/{stationNumber}|{name}/[Data, Schema]/
"""
DEFAULT_BASE_LOCN = "/data/vista/"
DATA_DIR = "DataV1"
def ensureCacheLocation(config):
    # by default put datasets under /data/ named for the id of the dataset given in config["name"]; but config can override with 'baseLocation'
    baseLocation = DEFAULT_BASE_LOCN if "baseLocation" not in config else (config["baseLocation"] if config["baseLocation"][-1] == "/" else config["baseLocation"] + "/")
    if not os.path.isdir(baseLocation):
        os.mkdir(baseLocation)
    if "stationNumber" in config and "useStationNumberInLocation" in config and config["useStationNumberInLocation"]:
        vistaId = config["stationNumber"]
    else:
        vistaId = config["name"]
    cacheLocation = baseLocation + vistaId + "/" 
    if not os.path.isdir(cacheLocation):
        os.mkdir(cacheLocation)
    dataLocation = cacheLocation + DATA_DIR + "/"
    if not os.path.isdir(dataLocation):
        os.mkdir(dataLocation)
    schemaLocation = cacheLocation + "Schema/"
    if not os.path.isdir(schemaLocation):
        os.mkdir(schemaLocation)
    logLocation = cacheLocation + "CacherLogs/"
    if not os.path.isdir(logLocation):
        os.mkdir(logLocation)
    return cacheLocation, dataLocation, schemaLocation, logLocation # data and schema under it
    
def makeFMQLIF(config):
    # Should work for CSP and 'regular' REST endpoint
    if "fmqlEP" in config:
        fmqlIF = FMQLRESTIF(config["fmqlEP"], epWord=config["fmqlQuery"])
        logging.info("Using REST Interface {}".format(config["fmqlEP"]))
    else:
        if "broker" not in config:
            raise Exception("Exiting - invalid 'config': neither 'broker' nor REST ('fmqlEP') settings available")
        # Must a/c for cypher in OSEHRA being different than Cypher in regular production VISTA (or maybe not if Vagrant VISTA is changed!)
        osehraVISTA = config["broker"]["osehraVISTA"] if "osehraVISTA" in config["broker"] else False
        fmqlIF = FMQLBrokerIF(config["broker"]["hostname"], config["broker"]["port"], config["broker"]["access"], config["broker"]["verify"], osehraVISTA=osehraVISTA)
        logging.info("Using RPC Broker Interface {}:{}".format(config["broker"]["hostname"], config["broker"]["port"]))
    return fmqlIF

"""
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
"""
def configLogging(logDir, logLevel="DEBUG"):

    log = logging.getLogger('')
    
    try: 
         mlogLevel = {"DEBUG": logging.DEBUG, "INFO": logging.INFO}[logLevel]
         log.setLevel(mlogLevel)
    except:
         log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    format = logging.Formatter("%(levelname)s - %(message)s")
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = handlers.RotatingFileHandler("{}/{}".format(logDir, "cacherLog.out"), maxBytes=(1048576*5), backupCount=7)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(format)
    log.addHandler(fh)
    
# ############################## Cache Utils  ###################

# ... not yet used - may add to a menu below if this becomes a "cache manager too"
def purgeCache(cacheLocation):
    try:
        shutil.rmtree(cacheLocation)
        print "Purged cache", cacheLocation
        os.mkdir(cacheLocation)
    except:
        pass
        
"""
Can get all types and then get replyFiles per type
"""
def typesInCache(cacheLocation):
    # a/c for _ and pure \d file types
    types = sorted(list(set(fl.split("-")[0] for fl in os.listdir(cacheLocation) if os.path.isfile(os.path.join(cacheLocation, fl)) and re.match(r'_?\d', fl) and re.search('\.json$', fl))))
    return types
        
def replyFilesOfType(cacheLocation, fileType):
    replyFiles = sorted([fl for fl in os.listdir(cacheLocation) if os.path.isfile(os.path.join(cacheLocation, fl)) and re.search('\.json$', fl) and re.match(fileType + "-", fl)], key=lambda x: float(re.search(r'\-([\d\.]+)\.json$', x).group(1)))
    return replyFiles

# ############################# Driver ####################################
    
CONFIGS = "/data/cacherConfigs/"
    
# Relies on configs in configs directory: ./cacher.py VISTAAB SCHEMA
def main():

    if not os.path.isdir(CONFIGS):
        print "No CONFIGS directory. Expected a {} with configurations - exiting".format(CONFIGS)
        return

    if len(sys.argv) < 2:
        print "need to specify configuration in 'configs/' ex/ VISTAAB - exiting"
        return

    config = sys.argv[1].split(".")[0]

    configsAvailable = [f.split(".")[0] for f in os.listdir(CONFIGS)]

    if config not in configsAvailable:
        print "config specified", config, "is not in 'configs/' but these are -", configsAvailable, "- exiting"
        return

    configJSON = json.load(open(CONFIGS + config + ".json"), object_pairs_hook=OrderedDict)

    print
    print "FMQL Caching using configuration", configJSON["name"], "..."
    if len(sys.argv) == 3 and sys.argv[2] == "SCHEMA":
        print "\tcaching schema"
        cacheSchemas(configJSON)
        return
    print
    print "Now caching data ..."
    cacheData(configJSON)
    print

if __name__ == "__main__":
    main()

