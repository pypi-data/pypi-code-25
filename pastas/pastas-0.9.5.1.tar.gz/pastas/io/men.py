"""This file contains the export method for men-files.

Export a .men file

R.C. Caljé - march 2018

"""

import pandas as pd
import numpy as np
import scipy.io as sio
import os
from ..utils import datetime2matlab

def load(fname):
    raise(NotImplementedError('This is not implemented yet. See the reads-section for a Menyanthes-read'))


def dump(fname, data, version=3):
    # version can also be a specific version, like '2.x.g.t (beta)', or an integer (see below)
    if version == 3:
        version = '3.x.b.c (gamma)'
    elif version == 2:
        version = '2.x.g.t (beta)'
    # load an empty menyanthes file
    io_dir, this_script_name = os.path.split(__file__)
    base_fname = os.path.join(io_dir,'men',version + '.men')
    assert os.path.exists(base_fname),'No Menyanthes file found for version ' + version
    men = sio.loadmat(base_fname,matlab_compatible=True)
    
    # add the oseries
    dtypeH = men['H'].dtype
    fields = dtypeH.fields.keys()
    Hdict={}
    for field in fields:
        if field == 'ID':
            Hdict[field] = men['ID']['H'][0][0][0][0]
            men['ID']['H']+=1
        elif field == 'Name':
            Hdict[field] = data['oseries']['name']
        elif field in ['NITGCode','OLGACode','NITGnr','OLGAnr']:
            Hdict[field] = '<no data> (1)'
        elif field == 'Type':
            Hdict[field] = 'Head'
        elif field in ['Project','layercode','LoggerSerial','area','datlog_serial']:
            Hdict[field] = ''
        elif field == 'values':
            date = np.array([datetime2matlab(x) for x in data['oseries']['series'].index])
            vals = data['oseries']['series'].values
            Hdict[field] = [np.vstack((date,vals)).transpose()]
        elif field == 'filtnr':
            Hdict[field] = 1
        elif field in ['handmeas','aerialphoto','BWImage','photo']:
            Hdict[field] = [np.zeros(shape=(0,0))]
        elif field in ['LastTUFExport','surflev','measpointlev','upfiltlev','lowfiltlev','sedsumplength','LoggerDepth','tranche','datlog_depth']:
            Hdict[field] = np.NaN
        elif field == 'xcoord':
            if 'x' in data['oseries']['metadata']:
                Hdict[field] = data['oseries']['metadata']['x']
            else:
                Hdict[field] = np.NaN
        elif field == 'ycoord':
            if 'y' in data['oseries']['metadata']:
                Hdict[field] = data['oseries']['metadata']['y']
            else:
                Hdict[field] = np.NaN
        elif field == 'date':
            Hdict[field] = datetime2matlab(pd.datetime.now())
        elif field == 'comment':
            #Hdict[field] = [np.array(['',''])]
            obj_arr = np.zeros((2,), dtype=np.object)
            obj_arr[0] = ''
            obj_arr[1] = ''
            Hdict[field] = [obj_arr]
        elif field in ['LoggerBrand','LoggerType','VegTypo','VegType','Organization']:
            Hdict[field] = 'Unknown'
        elif field == 'Status':
            Hdict[field] = 'Active'
        elif field == 'Comments':
            # TODO: has to be a matlab-table
            Hdict[field] = ''
        elif field == 'Meta':
            # TODO: has to be a matlab-table
            Hdict[field] = ''
        elif field == 'diver_files':
            # has to be a matlab-struct
            dtype=[('name', 'O'), ('LoggerSerial', 'O'), ('values', 'O'), ('orig_values', 'O'),
                   ('changes', 'O'), ('current_change', 'O'), ('drift', 'O'), ('importedby', 'O'),
                   ('importdate', 'O'), ('validated', 'O'), ('validatedby', 'O'), ('validatedate', 'O'),
                   ('battery_cap', 'O'), ('iscomp', 'O'), ('density', 'O'), ('compID', 'O'), ('ref', 'O'),
                   ('IsEquidistant', 'O'), ('IsLoggerfile', 'O'), ('timeshift', 'O')]
            Hdict[field] = [np.array([],dtype=dtype)]
        elif field == 'oldmetadata':
            # for version='2.x.g.t (beta)'
            dtype=[('xcoord', 'O'), ('ycoord', 'O'), ('upfiltlev', 'O'), ('lowfiltlev', 'O'),
                   ('surflev', 'O'), ('measpointlev', 'O'), ('sedsumplength', 'O'), ('datlog_serial', 'O'),
                   ('datlog_depth', 'O'), ('date', 'O'), ('comment', 'O'), ('LoggerBrand', 'O'),
                   ('LoggerType', 'O'), ('VegTypo', 'O'), ('VegType', 'O')]
            Hdict[field] = [np.array([],dtype=dtype)]
            
        else:
            raise(ValueError('Unknown field ' + field))
		
    Hnew = np.zeros((1,), dtype=dtypeH)
    for key,val in Hdict.items():
        Hnew[key] = val
    men['H']=np.vstack((men['H'],Hnew))
    
    # add the stressmodels
    dtypeIN = men['IN'].dtype
    fields = dtypeIN.fields.keys()
    for key in data['stressmodels'].keys():
        sm = data['stressmodels'][key]
        for istress, stress in enumerate(sm['stress']):
            INdict={}
            for field in fields:
                if field == 'ID':
                    INdict[field] = men['ID']['IN'][0][0][0][0]
                    men['ID']['IN']+=1
                elif field == 'Name':
                    INdict[field] = stress['name']
                elif field == 'Type':
                    if sm['stressmodel']=='StressModel2' and istress==1:
                        INdict[field] = 'EVAP'
                    else:
                        INdict[field] = 'PREC'
                elif field in ['LoggerSerial','datlog_serial']:
                    INdict[field] = ''
                elif field == 'values':
                    date = np.array([datetime2matlab(x) for x in stress['series'].index])
                    vals = stress['series'].values
                    INdict[field] = [np.vstack((date,vals)).transpose()]
                elif field == 'filtnr':
                    INdict[field] = 1
                elif field in ['surflev','upfiltlev','lowfiltlev']:
                    INdict[field] = np.NaN
                elif field == 'xcoord':
                    INdict[field] = np.NaN
                elif field == 'ycoord':
                    INdict[field] = np.NaN
                elif field == 'date':
                    INdict[field] = datetime2matlab(pd.datetime.now())
                elif field == 'Meta':
                    # TODO: has to be a matlab-table
                    INdict[field] = ''
                else:
                    raise(ValueError('Unknown field ' + field))
            INnew = np.zeros((1,), dtype=dtypeIN)
            for key,val in INdict.items():
                INnew[key] = val
            men['IN']=np.vstack((men['IN'],INnew))
    
    if False:
        # correct an error from loadmat
        if 'AutoImport' in men['PS'].dtype.fields.keys():
            for i in range(len(men['PS']['AutoImport'][0][0][0])):
                men['PS']['AutoImport'][0][0][0][i]['IsEnabled']=0
        men['PS']['AutoLocalExportEnabled']=False
        men['PS']['DrainVisEnabled']=False
        if 'RemoteDb' in men['PS'].dtype.fields.keys():
            men['PS']['RemoteDb'][0][0]['IsConnected']=0
        
        for key in men['ID'].dtype.fields.keys():
            men['ID'][key]=0
            
    # currently does not generate a model yet
    
    # save the file
    if not fname.endswith('.men'):
        fname = fname + '.men'
    sio.savemat(fname,men,appendmat=False)
    return print("%s file succesfully exported" % fname)
