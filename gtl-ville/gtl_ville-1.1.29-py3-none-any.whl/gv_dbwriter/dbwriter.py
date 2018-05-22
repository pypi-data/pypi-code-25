#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import os
import re

import psycopg2
import psycopg2.extras as psycopg2_extra

from gv_utils.enums import DataStructure
from gv_utils import datetime


class DBWriter:

    def __init__(self, dbhost, dbport, dbuser, dbpass, dbname):
        self.dbconn = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpass, host=dbhost, port=dbport)
        self.dbconn.autocommit = True
        self.sourcemap = {}
        self.cpmap = {}
        self.sectionmap = {}
        self.zonemap = {}

    def add_sections_cps(self, sectionscps):
        if type(sectionscps) is not dict:
            print('type(sectionscps) is not dict')
            return -1

        sections = sectionscps.get(DataStructure.SECTIONS.value, [])
        validfrom = sectionscps.get(DataStructure.VALIDFROM.value, 0)
        self.__fast_insert(lambda sectioncps: self.__add_section_cps(sectioncps, validfrom), sections,
                           """INSERT INTO section_cp (section_id, cp_id, valid_from) VALUES %s;""")

    def add_zones_sections(self, zonessections):
        if type(zonessections) is not dict:
            print('type(zonessections) is not dict')
            return -1

        zones = zonessections.get(DataStructure.ZONES.value)
        validfrom = zonessections.get(DataStructure.VALIDFROM.value)
        self.__fast_insert(lambda zonesections: self.__add_zone_sections(zonesections, validfrom), zones,
                           """INSERT INTO zone_section (zone_id, section_id, valid_from) VALUES %s;""")

    def add_cp_data(self, cpdata):
        if type(cpdata) is not dict:
            print('type(cpdata) is not dict')
            return -1

        data = cpdata.get(DataStructure.DATA.value)
        datatimestamp = cpdata.get(DataStructure.DATATIMESTAMP.value)
        self.__fast_insert(lambda sample: self.__add_cp_sample(sample, datatimestamp), data,
                           """INSERT INTO cp_data (cp_id, data_timestamp, data) VALUES %s;""")

    def add_section_data(self, sectiondata):
        if type(sectiondata) is not dict:
            print('type(sectiondata) is not dict')
            return -1

        data = sectiondata.get(DataStructure.DATA.value)
        datatimestamp = sectiondata.get(DataStructure.DATATIMESTAMP.value)
        self.__fast_insert(lambda sample: self.__add_section_sample(sample, datatimestamp), data,
                           """INSERT INTO section_data (section_id, data_timestamp, data) VALUES %s;""")

    def add_zone_data(self, zonedata):
        if type(zonedata) is not dict:
            print('type(zonedata) is not dict')
            return -1

        data = zonedata.get(DataStructure.DATA.value)
        datatimestamp = zonedata.get(DataStructure.DATATIMESTAMP.value)
        self.__fast_insert(lambda sample: self.__add_zone_sample(sample, datatimestamp), data,
                           """INSERT INTO zone_data (zone_id, data_timestamp, data) VALUES %s;""")

    def add_cluster_data(self, clusterdata):
        if type(clusterdata) is not dict:
            print('type(clusterdata) is not dict')
            return -1

        data = clusterdata.get(DataStructure.DATA.value)
        datatimestamp = clusterdata.get(DataStructure.DATATIMESTAMP.value)
        self.__fast_insert(lambda sample: self.__add_cluster_sample(sample, datatimestamp), data,
                           """INSERT INTO cluster_data (section_ids, geom, data_timestamp, data) VALUES %s;""")

    def __fast_insert(self, func, data, sqlcommand):
        cpu = os.cpu_count()
        with ThreadPoolExecutor(cpu) as executor:
            sqlvalues = executor.map(func, data)
        psycopg2_extra.execute_values(self.dbconn.cursor(), sqlcommand, filter(None, sqlvalues))

    # DB METHODS
    def __add_cp(self, cp):
        cpeid = cp.get(DataStructure.EID.value)
        if cpeid is not None:
            cur = self.dbconn.cursor()
            sourcename = cp.get(DataStructure.SOURCE.value, {}).get(DataStructure.NAME.value)
            if sourcename is not None:
                sourceid = self.sourcemap.get(sourcename) if sourcename in self.sourcemap \
                    else self.__insert_source(cur, sourcename)
                if sourceid is not None:
                    cpmap = self.cpmap.get(sourceid, {})
                    cpid = cpmap.get(cpeid) if cpeid in cpmap else self.__insert_cp(cur, cpeid, sourceid)
                    if cpid is not None:
                        cpgeom = cp.get(DataStructure.GEOM.value)
                        if cpgeom is not None:
                            self.__insert_cp_geom(cur, cpid, cpgeom)
                        else:
                            print('cpgeom is None')
                        cpatt = cp.get(DataStructure.ATT.value)
                        if bool(cpatt):
                            self.__insert_cp_att(cur, cpid, cpatt)
                        else:
                            print('not bool(cpatt)')
                        return cpid
                    else:
                        print('cpid is None')
                else:
                    print('sourceid is None')
            else:
                print('sourcename is None')
        else:
            print('cpeid is None')

    def __add_section(self, section):
        sectioneid = section.get(DataStructure.EID.value)
        if sectioneid is not None:
            cur = self.dbconn.cursor()
            sectioneid = re.sub("['\s+]", "", str(sectioneid))
            sectionmap = self.sectionmap
            sectionid = sectionmap.get(sectioneid) if sectioneid in sectionmap else self.__insert_section(cur,
                                                                                                          sectioneid)
            if sectionid is not None:
                sectiongeom = section.get(DataStructure.GEOM.value)
                if sectiongeom is not None:
                    self.__instert_section_geom(cur, sectionid, sectiongeom)
                else:
                    print('sectiongeom is None')
                sectionatt = section.get(DataStructure.ATT.value)
                if bool(sectionatt):
                    self.__insert_section_att(cur, sectionid, sectionatt)
                else:
                    print('not bool(sectionatt)')
                return sectionid
            else:
                print('sectionid is None')
        else:
            print('sectioneid is None')

    def __add_section_cps(self, sectioncps, validfrom):
        section = sectioncps.get(DataStructure.SECTION.value, {})
        sectioneid = section.get(DataStructure.EID.value)
        if sectioneid is not None:
            sectioneid = re.sub("['\s+]", "", str(sectioneid))
            sectionid = self.sectionmap.get(sectioneid) if sectioneid in self.sectionmap \
                else self.__add_section(section)
            if sectionid is not None:
                for sourcename, cpeids in sectioncps.get(DataStructure.CPIDS.value, {}).items():
                    sourceid = self.sourcemap.get(sourcename)
                    if sourceid is not None:
                        cpmap = self.cpmap.get(sourceid, {})
                        for cpeid in cpeids:
                            cpid = cpmap.get(cpeid)
                            if cpid is not None:
                                return sectionid, cpid, datetime.from_timestamp(validfrom, True)
                            else:
                                print('cpid is None')
                    else:
                        print('sourceid is None')
            else:
                print('sectionid is None')
        else:
            print('sectioneid is None')

    def __add_zone(self, zone):
        zoneeid = zone.get(DataStructure.EID.value)
        if zoneeid is not None:
            cur = self.dbconn.cursor()
            zonemap = self.zonemap
            zoneid = zonemap.get(zoneeid) if zoneeid in zonemap else self.__insert_zone(cur, zoneeid)
            if zoneid is not None:
                zonegeom = zone.get(DataStructure.GEOM.value)
                if zonegeom is not None:
                    self.__instert_zone_geom(cur, zoneid, zonegeom)
                else:
                    print('zonegeom is None')
                zoneatt = zone.get(DataStructure.ATT.value)
                if bool(zoneatt):
                    self.__insert_zone_att(cur, zoneid, zoneatt)
                else:
                    print('not bool(zoneatt)')
                return zoneid
            else:
                print('zoneid is None')
        else:
            print('zoneeid is None')

    def __add_zone_sections(self, zonesections, validfrom):
        zone = zonesections.get(DataStructure.ZONE.value, {})
        zoneeid = zone.get(DataStructure.EID.value)
        if zoneeid is not None:
            zonemap = self.zonemap
            zoneid = zonemap.get(zoneeid) if zoneeid in zonemap else self.__add_zone(zone)
            if zoneid is not None:
                for sectioneid in zonesections.get(DataStructure.SECTIONIDS.value, []):
                    sectionid = self.sectionmap.get(sectioneid)
                    if sectionid is not None:
                        return zoneid, sectionid, datetime.from_timestamp(validfrom, True)
                    else:
                        print('sectionid is None')
            else:
                print('zoneid is None')
        else:
            print('zoneeid is None')

    def __add_cp_sample(self, cpsample, datatimestamp):
        data = cpsample.get(DataStructure.DATA.value)
        if bool(data):
            cp = cpsample.get(DataStructure.CP.value, {})
            cpeid = cp.get(DataStructure.EID.value)
            if cpeid is not None:
                sourcename = cp.get(DataStructure.SOURCE.value, {}).get(DataStructure.NAME.value)
                cpmap = self.cpmap.get(self.sourcemap.get(sourcename), {})
                cpid = cpmap.get(cpeid) if cpeid in cpmap else self.__add_cp(cp)
                if cpid is not None:
                    return cpid, datetime.from_timestamp(datatimestamp, True), psycopg2_extra.Json(data)
                else:
                    print('cpid is None')
            else:
                print('cpeid is None')
        else:
            print('not bool(data)')

    def __add_section_sample(self, sectionsample, datatimestamp):
        data = sectionsample.get(DataStructure.DATA.value)
        if bool(data):
            section = sectionsample.get(DataStructure.SECTION.value, {})
            sectioneid = section.get(DataStructure.EID.value)
            if sectioneid is not None:
                sectionid = self.sectionmap.get(sectioneid) if sectioneid in self.sectionmap \
                    else self.__add_section(section)
                if sectionid is not None:
                    return sectionid, datetime.from_timestamp(datatimestamp, True), psycopg2_extra.Json(data)
                else:
                    print('sectionid is None')
            else:
                print('sectioneid is None')
        else:
            print('not bool(data)')

    def __add_zone_sample(self, zonesample, datatimestamp):
        data = zonesample.get(DataStructure.DATA.value)
        if bool(data):
            zone = zonesample.get(DataStructure.ZONE.value, {})
            zoneeid = zone.get(DataStructure.EID.value)
            if zoneeid is not None:
                zoneid = self.zonemap.get(zoneeid) if zoneeid in self.zonemap else self.__add_zone(zone)
                if zoneid is not None:
                    return zoneid, datetime.from_timestamp(datatimestamp, True), psycopg2_extra.Json(data)
                else:
                    print('zoneid is None')
            else:
                print('zoneeid is None')
        else:
            print('not bool(data)')

    def __add_cluster_sample(self, clustersample, datatimestamp):
        data = clustersample.get(DataStructure.DATA.value)
        if bool(data):
            sectioneids = clustersample.get(DataStructure.SECTIONIDS.value, [])
            if bool(sectioneids):
                sectionids = []
                for sectioneid in sectioneids:
                    sectionid = self.sectionmap.get(sectioneid)
                    if sectionid is not None:
                        sectionids.append(sectionid)
                    else:
                        print('sectionid is None')
                if bool(sectionids):
                    return (sectionids, DBWriter.__add_srid(clustersample.get(DataStructure.GEOM.value)),
                            datetime.from_timestamp(datatimestamp, True), psycopg2_extra.Json(data))
                else:
                    print('not bool(sectionids)')
            else:
                print('not bool(sectioneids)')
        else:
            print('not bool(data)')

    def __insert_source(self, cur, sourcename):
        sql = """INSERT INTO source (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id;"""
        cur.execute(sql, (sourcename, ))
        sourceid = None
        try:
            sourceid = cur.fetchone()[0]
        except (psycopg2.ProgrammingError, IndexError):
            pass
        if sourceid is not None:
            self.sourcemap[sourcename] = sourceid
        else:
            print('sourceid is None')
        return sourceid

    def __insert_cp(self, cur, cpeid, sourceid):
        sql = """INSERT INTO collection_point (eid, source_id) VALUES (%s, %s) ON CONFLICT (eid, source_id) DO UPDATE SET eid=EXCLUDED.eid RETURNING id;"""
        cur.execute(sql, (cpeid, sourceid))
        cpid = None
        try:
            cpid = cur.fetchone()[0]
        except (psycopg2.ProgrammingError, IndexError):
            pass
        if cpid is not None:
            if sourceid in self.cpmap:
                self.cpmap[sourceid][cpeid] = cpid
            else:
                self.cpmap[sourceid] = {cpeid: cpid}
        else:
            print('cpid is None')
        return cpid

    @staticmethod
    def __insert_cp_geom(cur, cpid, cpgeom):
        sql = """INSERT INTO cp_geom (cp_id, geom) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        cur.execute(sql, (cpid, DBWriter.__add_srid(cpgeom)))

    @staticmethod
    def __insert_cp_att(cur, cpid, cpatt):
        sql = """INSERT INTO cp_att (cp_id, att) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        cur.execute(sql, (cpid, psycopg2_extra.Json(cpatt)))

    def __insert_section(self, cur, sectioneid):
        sql = """INSERT INTO section (eid) VALUES (%s) ON CONFLICT (eid) DO UPDATE SET eid=EXCLUDED.eid RETURNING id;"""
        cur.execute(sql, (sectioneid, ))
        sectionid = None
        try:
            sectionid = cur.fetchone()[0]
        except (psycopg2.ProgrammingError, IndexError):
            print('psycopg2.ProgrammingError, IndexError')
        if sectionid is not None:
            self.sectionmap[sectioneid] = sectionid
        else:
            print('sectionid is None')
        return sectionid

    @staticmethod
    def __instert_section_geom(cur, sectionid, sectiongeom):
        sql = """INSERT INTO section_geom (section_id, geom) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        cur.execute(sql, (sectionid, DBWriter.__add_srid(sectiongeom)))

    @staticmethod
    def __insert_section_att(cur, sectionid, sectionatt):
        sql = """INSERT INTO section_att (section_id, att) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        cur.execute(sql, (sectionid, psycopg2_extra.Json(sectionatt)))

    def __insert_zone(self, cur, zoneeid):
        sql = """INSERT INTO zone (eid) VALUES (%s) ON CONFLICT (eid) DO UPDATE SET eid=EXCLUDED.eid RETURNING id;"""
        cur.execute(sql, (zoneeid,))
        zoneid = None
        try:
            zoneid = cur.fetchone()[0]
        except (psycopg2.ProgrammingError, IndexError):
            print('psycopg2.ProgrammingError, IndexError')
        if zoneid is not None:
            self.zonemap[zoneeid] = zoneid
        else:
            print('zoneid is None')
        return zoneid

    @staticmethod
    def __instert_zone_geom(cur, zoneid, zonegeom):
        sql = """INSERT INTO zone_geom (zone_id, geom) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        cur.execute(sql, (zoneid, DBWriter.__add_srid(zonegeom)))

    @staticmethod
    def __insert_zone_att(cur, zoneid, zoneatt):
        sql = """INSERT INTO zone_att (zone_id, att) VALUES (%s, %s) ON CONFLICT DO NOTHING;"""
        cur.execute(sql, (zoneid, psycopg2_extra.Json(zoneatt)))

    @staticmethod
    def __add_srid(wkt):
        if 'SRID' not in wkt:
            wkt = 'SRID=4326;' + wkt
        return wkt
