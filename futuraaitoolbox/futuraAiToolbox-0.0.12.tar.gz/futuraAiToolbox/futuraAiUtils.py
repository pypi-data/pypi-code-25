import os
import traceback
import imp
import sys
import datetime
import pandas as pd
import numpy as np
import urllib

# set up data director
FUTURAWEBAPI = 'http://test.futura.ai/data/{}.txt'


def isSubList(subList, superList):
    """ finds the member of subList in the superList

    :param subList: list(a)
    :param superList:list(a)
    :returns: list(bool)
    :rtype: list(bool)

    """
    bIndex = {}
    for item, elt in enumerate(superList):
        if elt not in bIndex:
            bIndex[elt] = item
    return [bIndex.get(item, None) for item in subList]


def fillnans(inArr):
    ''' fills in (column-wise)value gaps with the most recent non-nan value.

    fills in value gaps with the most recent non-nan value.
    Leading nan's remain in place. The gaps are filled in only after the first non-nan entry.

    Args:
        inArr (list, numpy array)
    Returns:
        returns an array of the same size as inArr with the nan-values replaced by the most recent non-nan entry.

    '''
    inArr = inArr.astype(float)
    nanPos = np.where(np.isnan(inArr))
    nanRow = nanPos[0]
    nanCol = nanPos[1]
    myArr = inArr.copy()
    for i in range(len(nanRow)):
        if nanRow[i] > 0:
            myArr[nanRow[i], nanCol[i]] = myArr[nanRow[i] - 1, nanCol[i]]
    return myArr


def fillwith(field, lookup):
    ''' replaces nan entries of field, with values of lookup.

    Args:
        field (list, numpy array) : array whose nan-values are to be replaced
        lookup (list, numpy array) : array to copy values for placement in field

    Returns:
        returns array with nan-values replaced by entries in lookup.
    '''

    out = field.astype(float)
    nanPos = np.where(np.isnan(out))
    nanRow = nanPos[0]
    nanCol = nanPos[1]

    for i in range(len(nanRow)):
        out[nanRow[i], nanCol[i]] = lookup[nanRow[i] - 1, nanCol[i]]

    return out


def mkdir_safe(dataDir):
    """ Safer mkdir that checks before creation
    :param dataDir:path to create a directory
    :returns: tuple(oneOf["ok","already_existing", "error"],explanation)
    :rtype: tuple

    """
    try:
        if not os.path.isdir(dataDir):
            os.mkdir(dataDir)
            return ("ok", dataDir)
        else:
            return ("already_existing", dataDir)
    except Exception as e:
        return ("error", e)


def loadTradingSystem(tradingSystem):
    """ Loads the trading system as a python object from various formats
    :param tradingSystem: Maybe(str, classobj, instance)
    :returns: object
    :rtype: object

    """

    if type(tradingSystem) is str:
        tradingSystem = tradingSystem.replace('\\', '/')
    filePathFlag = False
    if str(type(tradingSystem)) == "<type 'classobj'>" or str(
            type(tradingSystem)) == "<type 'type'>":
        TSobject = tradingSystem()
    elif str(type(tradingSystem)) == "<type 'instance'>" or str(
            type(tradingSystem)) == "<type 'module'>":
        TSobject = tradingSystem
    elif os.path.isfile(tradingSystem):
        filePathFlag = True
        filePath = str(tradingSystem)
        tsFolder, tsName = os.path.split(filePath)
        print filePath
        try:
            TSobject = imp.load_source('tradingSystemModule', filePath)
        except Exception as e:
            print 'Error loading trading system'
            print str(e)
            print traceback.format_exc()
            raise
    else:
        print "Please input your trading system's file path or a callable object."
        raise (Exception("unknown trading system"))
    return TSobject


def loadData(marketList=None,
             dataToLoad=None,
             refresh=False,
             beginInSample=None,
             endInSample=None,
             dataDir='tickerData'):
    """ prepares and returns market data for specified markets.

        prepares and returns related to the entries in the dataToLoad list. When refresh is true, data is updated from the Futura.ai server. If inSample is left as none, all available data dates will be returned.

        Args:
            marketList (list): list of market data to be supplied
            dataToLoad (list): list of financial data types to load
            refresh (bool): boolean value determining whether or not to update the local data from the Futura.ai server.
            beginInSample (str): a str in the format of YYYYMMDD defining the begining of the time series
            endInSample (str): a str in the format of YYYYMMDD defining the end of the time series

        Returns:
            dataMap (dict): mapping all data types requested by dataToLoad. The data is returned as a numpy array or list and is ordered by marketList along columns and date along the row.

    Copyright Futura.ai LLC - March 2018

    :param marketList: 
    :param dataToLoad: 
    :param refresh: 
    :param beginInSample: 
    :param endInSample: 
    :param dataDir: 
    :returns: 
    :rtype: 

    """
    mkdir = mkdir_safe
    if marketList is None:
        print "warning: no markets supplied"
        return

    dataToLoad = set(dataToLoad)
    requiredData = set(
        ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'P', 'RINFO', 'p'])
    fieldNames = set()

    dataToLoad.update(requiredData)

    nMarkets = len(marketList)

    # set up data director
    mkdir(dataDir)

    for j in range(nMarkets):
        path = os.path.join(dataDir, marketList[j] + '.txt')

        # check to see if market data is present. If not (or refresh is true), download data from Futura.ai.
        if not os.path.isfile(path) or refresh:
            try:
                if False:  #sys.version_info > (2,7,9):
                    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                    data = urllib.urlopen(
                        'http://test.futura.ai/data/' + marketList[j] + '.txt',
                        context=gcontext).read()
                else:
                    data = urllib.urlopen('http://test.futura.ai//data/' +
                                          marketList[j] + '.txt').read()
                with open(path, 'w') as dataFile:
                    dataFile.write(data)
                print 'Downloading ' + marketList[j]

            except:
                print 'Unable to download ' + marketList[j]
                marketList.remove(marketList[j])
            finally:
                dataFile.close()

    print 'Loading Data...'
    sys.stdout.flush()
    dataMap = {}
    largeDateRange = range(
        datetime.datetime(1990, 1, 1).toordinal(),
        datetime.datetime.today().toordinal() + 1)
    DATE_Large = [
        int(datetime.datetime.fromordinal(j).strftime('%Y%m%d'))
        for j in largeDateRange
    ]

    # Loading all markets into memory.
    for i, market in enumerate(marketList):
        marketFile = os.path.join('tickerData', market + '.txt')
        data = pd.read_csv(marketFile, engine='c')
        data.columns = map(str.strip, data.columns)
        fieldNames.update(list(data.columns.values))
        data.set_index('DATE', inplace=True)
        data['DATE'] = data.index

        for j, dataType in enumerate(dataToLoad):
            if dataType == 'p':
                data.rename(columns={'p': 'P'}, inplace=True)
                dataType = 'P'

            if dataType != 'DATE' and dataType not in dataMap and dataType in data:
                dataMap[dataType] = pd.DataFrame(
                    index=DATE_Large, columns=marketList)
                dataMap[dataType][market] = data[dataType]

            elif dataType != 'DATE' and dataType in data:
                dataMap[dataType][market] = data[dataType]

    # get args that are not in requiredData and fieldsNames
    additionDataToLoad = dataToLoad.difference(requiredData.union(fieldNames))
    additionDataFailed = set([])
    for i, additionData in enumerate(additionDataToLoad):
        filePath = os.path.join('tickerData', additionData + '.txt')
        # check to see if data is present. If not (or refresh is true), download data from Futura.ai.
        if not os.path.isfile(filePath) or refresh:
            try:
                if False:  #sys.version_info > (2,7,9):
                    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                    data = urllib.urlopen(
                        FUTURAWEBAPI.format(additionData),
                        context=gcontext).read()
                else:
                    data = urllib.urlopen(
                        FUTURAWEBAPI.format(additionData)).read()
                with open(filePath, 'w') as dataFile:
                    dataFile.write(data)
                print 'Downloading ' + additionData
            except:
                print 'Unable to download ' + additionData
                additionDataFailed.add(additionData)
                continue
            finally:
                dataFile.close()

        # read data from text file and load to memory
        data = pd.read_csv(filePath, engine='c')
        data.columns = map(str.strip, data.columns)
        data.set_index('DATE', inplace=True)
        data['DATE'] = data.index
        for j, column in enumerate(data.columns):
            if column != 'DATE':
                if additionData not in dataMap:
                    columns = set(data.columns)
                    columns.remove('DATE')
                    dataMap[additionData] = pd.DataFrame(
                        index=DATE_Large, columns=columns)
                dataMap[additionData][column] = data[column]

    additionDataToLoad = additionDataToLoad.difference(additionDataFailed)
    # fill the gap for additional data for the whole data range
    for i, additionData in enumerate(additionDataToLoad):
        dataMap[additionData][:] = fillnans(dataMap[additionData].values)

    # drop rows in CLOSE if none of the markets have data on that date
    dataMap['CLOSE'].dropna(how='all', inplace=True)

    # In-sample date management.
    if beginInSample is not None:
        beginInSample = datetime.datetime.strptime(beginInSample, '%Y%m%d')
    else:
        beginInSample = datetime.datetime(1990, 1, 1)
    beginInSampleInt = int(beginInSample.strftime('%Y%m%d'))

    if endInSample is not None:
        endInSample = datetime.datetime.strptime(endInSample, '%Y%m%d')
        endInSampleInt = int(endInSample.strftime('%Y%m%d'))
        dataMap['DATE'] = dataMap['CLOSE'].loc[beginInSampleInt:
                                               endInSampleInt, :].index.values
    else:
        dataMap['DATE'] = dataMap['CLOSE'].loc[
            beginInSampleInt:, :].index.values

    for index, dataType in enumerate(dataToLoad):
        if dataType != 'DATE' and dataType in dataMap:
            dataMap[dataType] = dataMap[dataType].loc[dataMap['DATE'], :]
            dataMap[dataType] = dataMap[dataType].values

    if 'VOL' in dataMap:
        dataMap['VOL'][np.isnan(dataMap['VOL'].astype(float))] = 0.0
    if 'OI' in dataMap:
        dataMap['OI'][np.isnan(dataMap['OI'].astype(float))] = 0.0
    if 'R' in dataMap:
        dataMap['R'][np.isnan(dataMap['R'].astype(float))] = 0.0
    if 'RINFO' in dataMap:
        dataMap['RINFO'][np.isnan(dataMap['RINFO'].astype(float))] = 0.0
        dataMap['RINFO'] = dataMap['RINFO'].astype(float)
    if 'P' in dataMap:
        dataMap['P'][np.isnan(dataMap['P'].astype(float))] = 0.0

    dataMap['CLOSE'] = fillnans(dataMap['CLOSE'])

    dataMap['OPEN'], dataMap['HIGH'], dataMap['LOW'] = fillwith(
        dataMap['OPEN'], dataMap['CLOSE']), fillwith(
            dataMap['HIGH'], dataMap['CLOSE']), fillwith(
                dataMap['LOW'], dataMap['CLOSE'])

    print '\bDone! \n',
    sys.stdout.flush()

    return dataMap
