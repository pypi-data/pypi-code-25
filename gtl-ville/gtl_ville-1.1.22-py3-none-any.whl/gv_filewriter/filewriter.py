#!/usr/bin/env python3

import asyncio
import bz2
import functools
import os

import aiofiles
import gv_protobuf.data_pb2 as gv_pb_data
from gv_utils import datetime
from gv_utils.enums import RedisData

DATA_PATH_STRUCT = '%Y/%m/%d/%H-%M.pb.gz2'


async def async_write_cluster_data(basepath, clusterdata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__cluster_data_to_pb, clusterdata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


async def async_write_cp_data(basepath, cpdata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__cp_data_to_pb, cpdata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


async def async_write_section_data(basepath, sectiondata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__section_data_to_pb, sectiondata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


async def async_write_zone_data(basepath, zonedata):
    loop = asyncio.get_event_loop()
    pbdata, datatimestamp = await loop.run_in_executor(None,
                                                       functools.partial(__cluster_data_to_pb, zonedata))
    await __async_write_pb_data(basepath, pbdata, datatimestamp)


def write_cluster_data(basepath, clusterdata):
    __write_pb_data(basepath, *__cluster_data_to_pb(clusterdata))


def write_cp_data(basepath, cpdata):
    __write_pb_data(basepath, *__cp_data_to_pb(cpdata))


def write_section_data(basepath, sectiondata):
    __write_pb_data(basepath, *__section_data_to_pb(sectiondata))


def write_zone_data(basepath, zonedata):
    __write_pb_data(basepath, *__cluster_data_to_pb(zonedata))


def read_cluster_data(pbpath):
    pbdata = gv_pb_data.ClusterData()
    pbdata.ParseFromString(__read_bytes(pbpath))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            RedisData.CLUSTER.value: {
                RedisData.SECTIONIDS.value: []
            },
            RedisData.GEOM.value: pbsample.cluster.geom,
            RedisData.ATT.value: dict(),
            RedisData.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        RedisData.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        RedisData.DATA.value: samples
    }


def read_cp_data(pbpath):
    pbdata = gv_pb_data.CpData()
    pbdata.ParseFromString(__read_bytes(pbpath))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            RedisData.CP.value: {
                RedisData.EID.value: str(pbsample.cp.eid),
                RedisData.SOURCE.value: {
                    RedisData.NAME.value: str(pbsample.cp.sourcename)
                }
            },
            RedisData.GEOM.value: pbsample.cp.geom,
            RedisData.ATT.value: dict(),
            RedisData.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        RedisData.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        RedisData.DATA.value: samples
    }


def read_section_data(pbpath):
    pbdata = gv_pb_data.SectionData()
    pbdata.ParseFromString(__read_bytes(pbpath))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            RedisData.SECTION.value: {
                RedisData.EID.value: str(pbsample.section.eid)
            },
            RedisData.GEOM.value: pbsample.section.geom,
            RedisData.ATT.value: dict(),
            RedisData.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        RedisData.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        RedisData.DATA.value: samples
    }


def read_zone_data(pbpath):
    pbdata = gv_pb_data.ZoneData()
    pbdata.ParseFromString(__read_bytes(pbpath))
    samples = []
    for pbsample in pbdata.sample:
        samples.append({
            RedisData.ZONE.value: {
                RedisData.SECTIONIDS.value: []
            },
            RedisData.GEOM.value: pbsample.cluster.geom,
            RedisData.ATT.value: dict(),
            RedisData.DATA.value: dict([(str(metric), float(pbsample.data[metric])) for metric in pbsample.data])
        })
    return {
        RedisData.DATATIMESTAMP.value: int(pbdata.timestamp.ToSeconds()),
        RedisData.DATA.value: samples
    }


def __cluster_data_to_pb(clusterdata):
    clustersamples, datatimestamp = __get_samples_timestamp(clusterdata)

    pbdata = gv_pb_data.ClusterData()

    for sample in clustersamples:
        pbsample = pbdata.sample.add()
        pbsample.cluster.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __cp_data_to_pb(cpdata):
    cpsamples, datatimestamp = __get_samples_timestamp(cpdata)

    pbdata = gv_pb_data.CpData()

    for sample in cpsamples:
        pbsample = pbdata.sample.add()
        cp = sample.get(RedisData.CP.value, {})
        pbsample.cp.eid = cp.get(RedisData.EID.value)
        pbsample.cp.sourcename = cp.get(RedisData.SOURCE.value, {}).get(RedisData.NAME.value)
        pbsample.cp.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __section_data_to_pb(sectiondata):
    sectionsamples, datatimestamp = __get_samples_timestamp(sectiondata)

    pbdata = gv_pb_data.SectionData()

    for sample in sectionsamples:
        pbsample = pbdata.sample.add()
        pbsample.section.eid = sample.get(RedisData.SECTION.value, {}).get(RedisData.EID.value)
        pbsample.section.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __zone_data_to_pb(zonedata):
    zonesamples, datatimestamp = __get_samples_timestamp(zonedata)

    pbdata = gv_pb_data.ZoneData()

    for sample in zonesamples:
        pbsample = pbdata.sample.add()
        pbsample.zone.geom = sample.get(RedisData.GEOM.value)
        __add_sample_metrics(pbsample, sample.get(RedisData.DATA.value, {}))

    pbdata.timestamp.FromSeconds(datatimestamp)
    return pbdata, datatimestamp


def __get_samples_timestamp(dictdata):
    if type(dictdata) is not dict:
        return [], datetime.now(roundtominute=True).timestamp()

    datatimestamp = dictdata.get(RedisData.DATATIMESTAMP.value, datetime.now(roundtominute=True).timestamp())
    samples = dictdata.get(RedisData.DATA.value, [])
    if type(samples) is not list:
        samples = []
    return samples, int(datatimestamp)


def __add_sample_metrics(sample, metrics):
    for metric, value in metrics.items():
        sample.data[metric] = float(value)


async def __async_write_pb_data(basepath, pbdata, datatimestamp):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, pbdata.SerializeToString)
    await __async_write_bytes(__get_full_path(basepath, datatimestamp), data)


def __write_pb_data(basepath, pbdata, datatimestamp):
    __write_bytes(__get_full_path(basepath, datatimestamp), pbdata.SerializeToString())


def __get_full_path(basepath, datatimestamp):
    fullpath = os.path.join(basepath,
                            datetime.from_timestamp(datatimestamp, roundtominute=True).strftime(DATA_PATH_STRUCT))
    directorypath = os.path.dirname(fullpath)
    if not os.path.exists(directorypath):
        os.makedirs(directorypath)
    return fullpath


async def async_write_graph(path, graphasyaml):
    await __async_write_bytes(path, graphasyaml)


def write_graph(path, graphasyaml):
    __write_bytes(path, graphasyaml)


async def __async_write_bytes(path, bytesdata):
    loop = asyncio.get_event_loop()
    compressdata = await loop.run_in_executor(None, functools.partial(bz2.compress, bytesdata))
    async with aiofiles.open(path, 'wb') as file:
        await file.write(compressdata)


def __write_bytes(path, bytesdata):
    with open(path, 'wb') as file:
        file.write(bz2.compress(bytesdata))


async def async_read_graph(path):
    return await __async_read_bytes(path)


def read_graph(path):
    return __read_bytes(path)


async def __async_read_bytes(path):
    loop = asyncio.get_event_loop()
    async with aiofiles.open(path, 'rb') as file:
        compressdata = await file.read()
    return await loop.run_in_executor(None, functools.partial(bz2.decompress, compressdata))


def __read_bytes(path):
    with open(path, 'rb') as file:
        return bz2.decompress(file.read())
