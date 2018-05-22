'''
Open Charge Map - Python Library
Written By: Jeremy Banker - loredous@loredous.net

Open Charge Map API Documentation - https://openchargemap.org/site/develop/api
'''
import logging
import urllib.parse
import uuid
from datetime import datetime

from requests import get

# Constants

_BASEURL = 'https://api.openchargemap.io/v2/'



class Ocmpy(object):
    logger = logging.getLogger('Ocmpy')

    def __init__(self, debug=False):
        self._connectionOpen = False
        if debug:
            logging.basicConfig(level=logging.DEBUG)

    def open(self):
        try:
            response = get(_BASEURL)
            if response.status_code is 200:
                self._loadreferencedata()
                self._connectionOpen = True
                return True
        except:
            raise OcmpyOpenFailed

    def getstations(self, ocmpyargs):
        """
        :type ocmpyargs: OcmpyArgs
        """
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        if not isinstance(ocmpyargs, OcmpyArgs):
            raise OcmpyInvalidArgs
        response = get(self._buildurl('poi/', ocmpyargs.dict))
        if not response.status_code is 200:
            raise OcmpyGetFailed('Get POI failed with response %d' % response.status_code)
        self.logger.debug('JSON Data: %s' % response.json())
        stations = [OcmpyStation(x, self) for x in response.json()]
        return stations

    def getstationsbylocation(self, lat, lon, dist=10, maxresults=10):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        oarg = OcmpyArgs(longitude=lon, latitude=lat, distance=dist, verbose=False, compact=True, maxresults=maxresults)
        return self.getstations(oarg)

    def _buildurl(self, path, args):
        return '{}{}?{}'.format(_BASEURL, path, urllib.parse.urlencode(args))

    def _loadreferencedata(self):
        response = get(_BASEURL + 'referencedata/')
        if not response.status_code is 200:
            raise OcmpyLoadReferenceDataFailed
        self._parsereferencedata(response.json())

    def _parsereferencedata(self, referencedata):
        try:
            self._chargertypesref = referencedata['ChargerTypes']
            self._connectiontypesref = referencedata['ConnectionTypes']
            self._currenttypesref = referencedata['CurrentTypes']
            self._countriesref = referencedata['Countries']
            self._dataprovidersref = referencedata['DataProviders']
            self._operatorsref = referencedata['Operators']
            self._statustypesref = referencedata['StatusTypes']
            self._submissionstatustypesref = referencedata['SubmissionStatusTypes']
            self._usagetypesref = referencedata['UsageTypes']
            self._usercommenttypesref = referencedata['UserCommentTypes']
            self._checkinstatustypesref = referencedata['CheckinStatusTypes']
            self._datatypesref = referencedata['DataTypes']
            self._metadatagroupsref = referencedata['MetadataGroups']
            return True

        except:
            raise OcmpyLoadReferenceDataFailed

    def lookupdataproviderbyid(self, dataproviderid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [provider for provider in self._dataprovidersref if provider['ID'] == dataproviderid]
        if not matches:
            raise OcmpyDataProviderNotFound('No data provider found for ID={}'.format(dataproviderid))
        return matches[0]

    def lookupoperatorbyid(self, operatorid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [operator for operator in self._operatorsref if operator['ID'] == operatorid]
        if not matches:
            raise OcmpyOperatorNotFound('No operator found for ID={}'.format(operatorid))
        return matches[0]

    def lookupusagetypebyid(self, usagetypeid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [usagetype for usagetype in self._usagetypesref if usagetype['ID'] == usagetypeid]
        if not matches:
            raise OcmpyUsageTypeNotFound('No usage type found for ID={}'.format(usagetypeid))
        return matches[0]

    def lookupcountrybyid(self, countryid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [country for country in self._countriesref if country['ID'] == countryid]
        if not matches:
            raise OcmpyCountryNotFound('No country found for ID={}'.format(countryid))
        return matches[0]

    def lookupstatustypebyid(self, statustypeid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        if statustypeid is None:
            statustypeid = 0
        matches = [statustype for statustype in self._statustypesref if statustype['ID'] == statustypeid]
        if not matches:
            raise OcmpyStatusTypeNotFound('No status type found for ID={}'.format(statustypeid))
        return matches[0]

    def lookupsubmissionstatustypebyid(self, submissionstatustypeid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [submissionstatustype for submissionstatustype in self._submissionstatustypesref
                   if submissionstatustype['ID'] == submissionstatustypeid]
        if not matches:
            raise OcmpySubmissionStatusTypeNotFound(
                'No submission status type found for ID={}'.format(submissionstatustypeid))
        return matches[0]

    def lookuplevelbyid(self, levelid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [level for level in self._chargertypesref if level['ID'] == levelid]
        if not matches:
            raise OcmpyLevelNotFound('No level found for ID={}'.format(levelid))
        return matches[0]

    def lookupconnectiontypebyid(self, connectiontypeid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [connectiontype for connectiontype in self._connectiontypesref
                   if connectiontype['ID'] == connectiontypeid]
        if not matches:
            raise OcmpyConnectionTypeNotFound('No connection type found for ID={}'.format(connectiontypeid))
        return matches[0]

    def lookupcurrenttypebyid(self, currenttypeid):
        if not self._connectionOpen:
            raise OcmpyNotOpen('Connection must be opened with open() before calling this method')
        matches = [currenttype for currenttype in self._currenttypesref if currenttype['ID'] == currenttypeid]
        if not matches:
            raise OcmpyCurrentTypeNotFound('No current type found for ID={}'.format(currenttypeid))
        return matches[0]

class OcmpyArgs(object):
    logger = logging.getLogger('OcmpyArgs')

    def __init__(self, maxresults=None, countrycode=None, latitude=None, longitude=None, distance=None,
                 distanceunit=None, operatorid=None, connectiontypeid=None, countryid=None, levelid=None,
                 minpowerkw=None, usagetypeid=None, statustypeid=None, dataproviderid=None, modifiedsince=None,
                 opendata=None, includecomments=None, verbose=None, compact=None, chargepointid=None):
        self.maxresults = maxresults
        self.countrycode = countrycode
        self.latitude = latitude
        self.longitude = longitude
        self.distance = distance
        self.distanceunit = distanceunit
        self.operatorid = operatorid
        self.connectiontypeid = connectiontypeid
        self.countryid = countryid
        self.levelid = levelid
        self.minpowerkw = minpowerkw
        self.usagetypeid = usagetypeid
        self.statustypeid = statustypeid
        self.dataproviderid = dataproviderid
        self.modifiedsince = modifiedsince
        self.opendata = opendata
        self.includecomments = includecomments
        self.verbose = verbose
        self.compact = compact
        self.chargepointid = chargepointid

    @property
    def dict(self):
        loc = dict(locals())
        for key in self.__dict__.keys():
            self.logger.debug('%s = %s', key, self.__getattribute__(key))
        return dict([(key, self.__getattribute__(key)) for key in self.__dict__.keys()
                     if not self.__getattribute__(key) is None])


class OcmpyStation(object):

    def __init__(self, stationdict, ocmpyinstance=None):
        self._ocmpyinstance = ocmpyinstance
        self._stationdict = stationdict
        self._parsestation(stationdict)


    def __str__(self):
        return 'Station ID: {}, Title: {}'.format(self._id, self._addresstitle)

    def __repr__(self):
        return 'OcmpyStation(ID={},Title={})'.format(self._id, self._addresstitle)

    def _parsestation(self, stationdict):
        try:
            self._id = stationdict['ID']
            self._uuid = stationdict.get('UUID', None)
            self._parentchargepointid = stationdict.get('ParentChargePointID', None)
            self._dataproviderid = stationdict.get('DataProviderID', None)
            self._operatorid = stationdict.get('OperatorID', None)
            self._operatorsreference = stationdict.get('OperatorsReference', None)
            self._usagetypeid = stationdict.get('UsageTypeID', None)
            self._usagecost = stationdict.get('UsageCost', None)
            self._numberofpoints = stationdict.get('NumberOfPoints', None)
            self._generalcomments = stationdict.get('GeneralComments', None)
            self._dateplanned = stationdict.get('DatePlanned', None)
            self._datelastconfirmed = stationdict.get('DateLastConfirmed', None)
            self._statustypeid = stationdict.get('StatusTypeID', None)
            self._datelaststatusupdate = stationdict.get('DateLastStatusUpdate', None)
            self._dataqualitylevel = stationdict.get('DataQualityLevel', None)
            self._datecreated = stationdict.get('DateCreated', None)
            self._submissionstatustypeid = stationdict.get('SubmissionStatusTypeID', None)
            self._percentagesimilarity = stationdict.get('PercentageSimilarity', None)
            self._isrecentlyverified = stationdict.get('IsRecentlyVerified', None)
            self._datelastverified = stationdict.get('DateLastVerified', None)

            # Connection Information
            self.Connections = list(OcmpyStationConnection(x, self._ocmpyinstance)
                                    for x in stationdict.get('Connections', []))

            # Address Information
            self._addressid = stationdict.get('AddressInfo', {}).get('ID', None)
            self._addresstitle = stationdict.get('AddressInfo', {}).get('Title', None)
            self._addressline1 = stationdict.get('AddressInfo', {}).get('AddressLine1', None)
            self._addressline2 = stationdict.get('AddressInfo', {}).get('AddressLine2', None)
            self._addresstown = stationdict.get('AddressInfo', {}).get('Town', None)
            self._addressstateorprovince = stationdict.get('AddressInfo', {}).get('StateOrProvince', None)
            self._addresspostcode = stationdict.get('AddressInfo', {}).get('Postcode', None)
            self._addresscountryid = stationdict.get('AddressInfo', {}).get('CountryID', None)
            self._addresslatitude = stationdict.get('AddressInfo', {}).get('Latitude', None)
            self._addresslongitude = stationdict.get('AddressInfo', {}).get('Longitude', None)
            self._addresscontacttelephone1 = stationdict.get('AddressInfo', {}).get('ContactTelephone1', None)
            self._addressdistanceunit = stationdict.get('AddressInfo', {}).get('DistanceUnit', None)
        except:
            raise OcmpyLoadStationFailed

    @property
    def ID(self):
        return self._id

    @property
    def UUID(self):
        return uuid.UUID(self._uuid)

    @property
    def ParentChargePointID(self):
        return self._parentchargepointid

    @property
    def DataProviderID(self):
        return self._dataproviderid

    @property
    def DataProvider(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupdataproviderbyid(self._dataproviderid)

    @property
    def OperatorID(self):
        return self._operatorid

    @property
    def Operator(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupoperatorbyid(self._operatorid)

    @property
    def OperatorsReference(self):
        return self._operatorsreference

    @property
    def UsageTypeID(self):
        return self._usagetypeid

    @property
    def UsageType(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupusagetypebyid(self._usagetypeid)

    @property
    def AddressID(self):
        return self._addressid

    @property
    def Title(self):
        return self._addresstitle

    @property
    def AddressLine1(self):
        return self._addressline1

    @property
    def AddressLine2(self):
        return self._addressline2

    @property
    def Town(self):
        return self._addresstown

    @property
    def State(self):
        return self._addressstateorprovince

    @property
    def Province(self):
        return self._addressstateorprovince

    @property
    def Postcode(self):
        return self._addresspostcode

    @property
    def CountryID(self):
        return self._addresscountryid

    @property
    def Country(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupcountrybyid(self._addresscountryid)

    @property
    def PrintableAddress(self):
        addrstring = self._addresstitle + '\n'
        addrstring += self._addressline1 + '\n'
        if self._addressline2:
            addrstring += self._addressline2 + '\n'
        addrstring += self._addresstown + ', ' + self._addressstateorprovince + ' ' + self._addresspostcode + '\n'
        addrstring += self.Country.get('Title', '')
        return addrstring

    @property
    def Latitude(self):
        return self._addresslatitude

    @property
    def Longitude(self):
        return self._addresslongitude

    @property
    def Coordinates(self):
        return {'lat': self._addresslatitude, 'lon': self._addresslongitude}

    @property
    def ContactPhone(self):
        return self._addresscontacttelephone1

    @property
    def NumberOfChargePoints(self):
        return self._numberofpoints

    @property
    def GeneralComments(self):
        return self._generalcomments

    @property
    def StatusTypeID(self):
        return self._statustypeid

    @property
    def Status(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupstatustypebyid(self._statustypeid)

    @property
    def LastStatusUpdateDate(self):
        return datetime.strptime(self._datelaststatusupdate, '%Y-%m-%dT%H:%M:%SZ')

    @property
    def DataQualityLevel(self):
        return self._dataqualitylevel

    @property
    def DateCreated(self):
        return datetime.strptime(self._datecreated, '%Y-%m-%dT%H:%M:%SZ')

    @property
    def SubmissionStatusTypeID(self):
        return self._submissionstatustypeid

    @property
    def SubmissionStatus(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupsubmissionstatustypebyid(self._submissionstatustypeid)

    @property
    def RecentlyVerified(self):
        return self._isrecentlyverified

    @property
    def DateLastVerified(self):
        return datetime.strptime(self._datelastverified, '%Y-%m-%dT%H:%M:%SZ')


class OcmpyStationConnection(object):

    def __init__(self, connectiondict, ocmpyinstance):
        self._ocmpyinstance = ocmpyinstance
        self._connectiondict = connectiondict
        self._parseconnection(connectiondict)

    def _parseconnection(self, connectiondict):
        try:
            self._id = connectiondict['ID']
            self._connectiontypeid = connectiondict.get('ConnectionTypeID', None)
            self._reference = connectiondict.get('Reference', None)
            self._statustypeid = connectiondict.get('StatusTypeID', None)
            self._levelid = connectiondict.get('LevelID', None)
            self._amps = connectiondict.get('Amps', None)
            self._voltage = connectiondict.get('Voltage', None)
            self._powerkw = connectiondict.get('PowerKW', None)
            self._currenttypeid = connectiondict.get('CurrentTypeID', None)
            self._quantity = connectiondict.get('Quantity', None)
        except:
            raise OcmpyLoadConnectionFailed

    @property
    def ID(self):
        return self._id

    @property
    def ConnectionTypeID(self):
        return self._connectiontypeid

    @property
    def ConnectionType(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupconnectiontypebyid(self._connectiontypeid)

    @property
    def Reference(self):
        return self._reference

    @property
    def StatusTypeID(self):
        return self._statustypeid

    @property
    def Status(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupstatustypebyid(self._statustypeid)

    @property
    def LevelID(self):
        return self._levelid

    @property
    def Level(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookuplevelbyid(self._levelid)

    @property
    def PowerKW(self):
        return self._powerkw

    @property
    def CurrentTypeID(self):
        return self._currenttypeid

    @property
    def CurrentType(self):
        if self._ocmpyinstance is None:
            raise OcmpyInstanceNotSet(message='Must set a valid Ocmpy() instance before using lookup properties')
        return self._ocmpyinstance.lookupcurrenttypebyid(self._currenttypeid)

    @property
    def Quantity(self):
        return self._quantity


# Custom Exceptions


class OcmpyBaseException(Exception):
    pass


class OcmpyOpenFailed(OcmpyBaseException):
    pass


class OcmpyNotOpen(OcmpyBaseException):
    pass


class OcmpyInvalidArgs(OcmpyBaseException):
    pass


class OcmpyGetFailed(OcmpyBaseException):
    pass


class OcmpyLoadReferenceDataFailed(OcmpyBaseException):
    pass


class OcmpyLoadStationFailed(OcmpyBaseException):
    pass


class OcmpyInstanceNotSet(OcmpyBaseException):
    pass


class OcmpyDataProviderNotFound(OcmpyBaseException):
    pass


class OcmpyOperatorNotFound(OcmpyBaseException):
    pass


class OcmpyUsageTypeNotFound(OcmpyBaseException):
    pass


class OcmpyCountryNotFound(OcmpyBaseException):
    pass


class OcmpyStatusTypeNotFound(OcmpyBaseException):
    pass


class OcmpySubmissionStatusTypeNotFound(OcmpyBaseException):
    pass


class OcmpyLoadConnectionFailed(OcmpyBaseException):
    pass


class OcmpyLevelNotFound(OcmpyBaseException):
    pass


class OcmpyConnectionTypeNotFound(OcmpyBaseException):
    pass


class OcmpyCurrentTypeNotFound(OcmpyBaseException):
    pass