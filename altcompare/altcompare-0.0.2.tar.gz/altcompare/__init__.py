

import pandas as pd
import numpy as np
import pyodbc

def connectServer(driver, server, database, port=False, userid=False, password=False):
    userstr = ''
    portstr = ''
    if userid:
        userstr = 'uid=' + userid +'; pwd=' + password + ';'
    if port:
        portstr = 'port=' + str(int(port)) +';'

    if driver.upper() == 'SQLSERVER':
        driver = 'SQL Server Native Client 11.0'
    elif driver.upper() == 'SYBASE':
        driver = 'Adaptive Server Enterprise'
    # Throw error
    elif driver not in pyodbc.drivers():
        driver = 'SQL Server Native Client 11.0'

    connstr = "Driver=" + driver + "; Server=" + server +"; " + portstr + " Database=" + database + "; " + userstr + " Trusted_Connection=yes"
    return pyodbc.connect(connstr)

def connectServerFromCsv(conname):
    condata = pd.read_csv('Connections.csv')
    condata.fillna(False, inplace=True)
    conn = condata[condata['Name']==conname]
    return connectServer(conn.iloc[0].Driver,conn.iloc[0].Server, conn.iloc[0].Database, conn.iloc[0].Port, conn.iloc[0].UserID, conn.iloc[0].Password )

def getSQLData(query, conn, conntxt='data', dropcols=[], keepcols=[], nadata=''):
    tabdata =  pd.read_sql(query, conn)  
    tabdata.drop(dropcols, axis=1, inplace=True)
    if len(keepcols) != 0:
        tabdata = tabdata[keepcols]
    tabdata.fillna(nadata, inplace=True)
    tabdata['ENV'] = conntxt
    return tabdata

def getCSVData(filename, conntxt='data', colnames=[], dropcols=[], keepcols=[], header=None, skiprows=0, nadata=''):
    if len(colnames) != 0:
        tabdata = pd.read_csv(filename, header=header, skiprows=skiprows, names=colnames)
    else:    
        tabdata = pd.read_csv(filename)
    tabdata.drop(dropcols, axis=1, inplace=True)
    tabdata['ENV'] = 'PROD'
    if len(keepcols) != 0:
        tabdata = tabdata[keepcols]
    tabdata.fillna(nadata, inplace=True)
    tabdata['ENV'] = conntxt
    return tabdata

def compareData(data1, data2, dropcols=[], keepcols=[]):
    dataall = data1.append(data2)
    dataall.drop(dropcols, axis=1, inplace=True)
    dataall['COUNT'] = 1
    datacols = list(dataall)
    compcols = list(set(datacols).difference(set(['COUNT','ENV'])))
    datagrp = dataall.groupby(compcols).agg({'COUNT':'sum', 'ENV':'max'}).reset_index()
    datadup = datagrp[datagrp['COUNT'] != 2]
    return datadup

def compareColumns(data, keyfields, nadata=''):
    data.drop('COUNT', axis=1, inplace=True)
    meltkeys = keyfields
    meltkeys.append('ENV')
    datamelt = pd.melt(data, id_vars=meltkeys, var_name='Field', value_name='FieldVal')
    datamelt['COUNT'] = 1

    datamelt.fillna(nadata, inplace=True)
    datamelt.FieldVal = datamelt.FieldVal.astype(str)
    datamcols = list(datamelt)
    compmcols = list(set(datamcols).difference(set(['COUNT','ENV'])))
    datamgrp = datamelt.groupby(compmcols).agg({'COUNT':'sum', 'ENV':'max'}).reset_index()
    datamdup = datamgrp[datamgrp['COUNT'] != 2]
    othflds = set(keyfields).difference(set(['ENV']))
    keyfields.extend(['Field'])
    datapiv = pd.pivot_table(datamdup,index=othflds,values=['FieldVal'], columns=["ENV"], aggfunc=[np.max],fill_value='').reset_index()
    # datapiv =  datamdup.set_index(datamcols).unstack('ENV').reset_index()
    datapiv.columns = [''.join(col) for col in datapiv.columns]   
    return datapiv

def normalizeColumns(data, keyfields, nadata=''):
    datancols = list(data)
    normcols = list(set(datancols).difference(set(keyfields)))
    datapiv = pd.pivot_table(data,index=keyfields,values=normcols, columns=["ENV"], aggfunc=[np.max],fill_value='').reset_index()
    datapiv.columns = [''.join(col) for col in datapiv.columns]  
    return datapiv
