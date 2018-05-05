#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3
import json
from .data import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()


class EMT:
    """ This is EMT Class
       Methods:
           BUS:
               GetRouteLines
               GetRouteLinesRoute
               GetCalendar
               GetListLines
               GetListLinesExtend
               GetGroups
               GetTimesLines
               GetTimeTableLines
               GetNodesLines

            GEO:
                GetStreet
                GetStopsFromStop
                GetStopsFromXY
                GetArriveStop
                GetPointsOfInterest
                GetPointsOfInterestTypes
                getStreetFromXY
                GetInfoLine
                GetInfoLineExtend
                GetStopsLine
                GeoGetGroups

    """

    def __init__(self, idClient, passKey):
        """
        :param idClient: idClient provided by EMT
        :param passKey: passKey provided by EMT
        """
        self.acceso = {"idClient": idClient, "passKey": passKey}

    def request_api(self, url, payload):
        """
        Make the POST request to the URL and with the indicated parameters

        :param url: String
        :param payload: json dictionary
        :return: JSON
        """
        self.acceso.update(payload)

        try:
            response = http.request('POST', url, fields=self.acceso)
            data_json = json.loads(response.data.decode('utf-8'))

        except:
            data_json = "{'error':'Error processing the request.'}"

        return data_json

    def GetRouteLines(self, SelectDate, Lines):
        """
        The itinerary of a line is obtained, with the vertices to construct the straight lines of the route
        and the UTM coordinates of the road axes and the stop codes. (One way journeys.)

        :param date: Date with format dd/MM/yyyy
        :param lines: String whit the line or lines to consult separates with the character pipe(|).
        :return: JSON
        """
        payload = {"SelectDate": SelectDate, "Lines": Lines}
        return self.request_api(BUS_GETROUTELINES, payload)

    def GetRouteLinesRoute(self, SelectDate, Lines):
        """
        The itinerary of a line is obtained, with the vertices to construct the lines of the route and the
        geographic coordinates of the road axes and the stop codes.

        :param date: Date with format dd/MM/yyyy
        :param lines: String whit the line or lines to consult separates with the character pipe(|).
        :return: JSON
        """
        payload = {"SelectDate": SelectDate, "Lines": Lines}
        return self.request_api(BUS_GETROUTELINESROUTE, payload)

    def GetCalendar(self, SelectDateBegin, SelectDateEnd):
        """
        Gets the EMT calendar of day types applicable to line schedules for a requested start-end range.

        :param datebegin: Date with format dd/MM/yyyy
        :param dateend: Date with format dd/MM/yyyy
        :return: JSON
        """

        payload = {"SelectDateBegin": SelectDateBegin, "SelectDateEnd": SelectDateEnd}
        return self.request_api(BUS_GETCALENDAR, payload)

    def GetListLines(self, SelectDate, Lines):
        """
        Retrieves the general relation of lines with their description and subgroup to which they belong.

        :param SelectDate: Date with format dd/MM/yyyy
        :param Lines: String whit the line or lines to consult separates with the character pipe(|).
        :return: JSON
        """

        payload = {"SelectDate": SelectDate, "Lines": Lines}
        return self.request_api(BUS_GETLISTLINES, payload)

    def GetListLinesExtend(self, SelectDate, Lines):
        """
        Retrieves the general relation of lines with their description and subgroup to which they belong.
        (Return more information that GetListLines())

        :param SelectDate: Date with format dd/MM/yyyy
        :param Lines: String whit the line or lines to consult separates with the character pipe(|).
        :return: JSON
        """

        payload = {"SelectDate": SelectDate, "Lines": Lines}
        return self.request_api(BUS_GETLISTLINESEXTEND, payload)

    def GetGroups(self):
        """
        It returns the data of the different types of networks of EMT lines (regular, university, night, etc.),
        together with their different breakdowns.

        :return: JSON
        """

        return self.request_api(BUS_GETGROUPS, {})

    def GetTimesLines(self, SelectDate, Lines):
        """
        Retrieves the current schedules for all day types of the requested lines.

        :param SelectDate: Date with format dd/MM/yyyy
        :param Lines: String whit the line or lines to consult separates with the character pipe(|).
        :return: JSON
        """

        payload = {"SelectDate": SelectDate, "Lines": Lines}
        return self.request_api(BUS_GETTIMESLINES, payload)

    def GetTimeTableLines(self, SelectDate, Lines):
        """
        Provide information of the requested line with a trip-level detail.

        :param SelectDate: Date with format dd/MM/yyyy
        :param Lines: String whit the line or lines to consult separates with the character pipe(|).
        :return: JSON
        """

        payload = {"SelectDate": SelectDate, "Lines": Lines}
        return self.request_api(BUS_GETTIMETABLELINES, payload)

    def GetNodesLines(self, Nodes):
        """
        Retrieve all stop identifiers, along with their UTM coordinate, name and the relationship of lines / direction
        that pass through each of them.

        :param Nodes: String Bus stop number of EMT.
        :return: JSON
        """

        payload = {"Nodes": Nodes}
        return self.request_api(BUS_GETNODESLINES, payload)

    def GetStreet(self, description, Radius, streetNumber='', cultureInfo='ES'):
        """
        Gets a list of EMT locations matching a location. Each site is composed of a list of EMT stops located within
        a predefined radius with all its attributes, as well as the EMT lines that pass through each stop in the list.

        :param description: String Name of the street
        :param Radius: String Radio of action in meters
        :param streetNumber: String Street number (Opcional)
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"description": description, "Radius": Radius, "streetNumber": streetNumber, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETSTREET, payload)

    def GetStopsFromStop(self, idStop, Radius, cultureInfo='ES'):
        """
        It obtains a list of EMT stops located from an EMT stop and within a predefined radius with all its attributes,
        in addition to the EMT lines that pass through each stop of the list.
        
        :param idStop: String EMT stop number
        :param Radius: Int Radio of action in meters
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"idStop": idStop, "Radius": Radius, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETSTOPFROMSTOP, payload)

    def GetStopsFromXY(self, latitude, longitude, Radius, cultureInfo='ES'):
        """
        It obtains a list of EMT stops located from a coordinate and within a predefined radius with all its attributes,
        in addition to the EMT lines that pass through each stop of the list.

        :param latitude: Double X coordinate of the place
        :param longitude: Double Y coordinate of the place
        :param Radius: Int Radio of action in meters
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"latitude": latitude, "longitude":longitude, "Radius": Radius,"cultureInfo": cultureInfo}
        return self.request_api(GEO_GETSTOPSFROMXY, payload)

    def GetArriveStop(self, idStop, cultureInfo='ES'):
        """
        Obtain the estimated arrival data of the bus at a specific stop

        :param idStop: String EMT stop number
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"idStop": idStop, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETARRIVESTOP, payload)

    def GetPointsOfInterest(self, latitude, longitude, Radius, tipos = '', cultureInfo='ES'):
        """
        Get the list of points of interest located from a coordinate and within a defined radius, along with their attributes

        :param latitude: Double X coordinate of the place
        :param longitude: Double Y coordinate of the place
        :param Radius: Int Radio of action in meters
        :param tipos: String types of points of interest (Opcional)
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"latitude": latitude, "longitude":longitude, "Radius": Radius, "tipos":tipos, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETPOINTSOFINTEREST, payload)

    def GetPointsOfInterestTypes(self):
        """
        Get the list of the types of points of interest

        :return: JSON
        """

        return self.request_api(GEO_GETPOINTSOFINTERESTTYPE, {})

    def getStreetFromXY(self, latitude, longitude, Radius, cultureInfo='ES'):
        """
        It obtains a list of streets located in a radius of n meters around the coordinate provided (the system accepts UTM and WSG84)

        :param latitude: Double X coordinate of the place
        :param longitude: Double Y coordinate of the place
        :param Radius: Int Radio of action in meters
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"latitude": latitude, "longitude": longitude, "Radius": Radius, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETSTREETFROMXY, payload)

    def GetInfoLine(self, date, line, cultureInfo='ES'):
        """
        Obtain the basic information of an EMT line at a given date

        :param date: Date with format dd/MM/yyyy
        :param line: String line number
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"date": date, "line": line, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETINFOLINE, payload)

    def GetInfoLineExtend(self, date, line, cultureInfo='ES'):
        """
        It is the same method as GetInfoLine but it provides advanced information about the published frequencies and
        other relevant data

        :param date: Date with format dd/MM/yyyy
        :param line: String line number
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"date": date, "line": line, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETINFOLINEEXTEND, payload)

    def GetStopsLine(self, line, direction, cultureInfo='ES'):
        """
        Obtain a list of EMT stops related to the requested line (optionally in the requested direction of travel)

        :param line: String line number
        :param direction: String Direction of travel (1: round 2: trip)
        :param cultureInfo: String If it is included, it may contain the EN value (The return of certain contents
        will be in English) ES (The return of certain contents will be in Spanish)(Opcional)
        :return: JSON
        """

        payload = {"line": line, "direction":direction, "cultureInfo": cultureInfo}
        return self.request_api(GEO_GETSTOPSLINE, payload)

    def GeoGetGroups(self):
        """
        Returns the relationship of exploitation groups

        :return: JSON
        """

        return self.request_api(GEO_GETGROUPS, {})

