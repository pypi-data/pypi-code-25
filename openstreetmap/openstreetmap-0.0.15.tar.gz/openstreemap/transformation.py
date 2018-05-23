# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
-------------------------------------------------
"""
import math

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def gcj02_to_bd09(lng, lat):
    """
    Mars coordinate system (GCJ-02) to Baidu coordinate system (BD-09)
    Google, GAD - > Baidu
    :param lng:Mars lng
    :param lat:Mars lat
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    Baidu coordinate system (BD-09) to  Mars coordinate system (GCJ-02)
    Baidu - > Google, Gao De
    :param bd_lat:Baidu lng
    :param bd_lon:Baidu lat
    :return:
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84 to GCJ02 (Mars coordinate system)
    :param lng:WGS84 lng
    :param lat:WGS84 lat
    :return:
    """
    # if out_of_china(lng, lat):
    #     return lng, lat
    d_lat = _trans_form_lat(lng - 105.0, lat - 35.0)
    d_lng = _trans_form_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * pi
    magic = math.sin(rad_lat)
    magic = 1 - ee * magic * magic
    sqrt_magic = math.sqrt(magic)
    d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * pi)
    d_lng = (d_lng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * pi)
    mg_lat = lat + d_lat
    mg_lng = lng + d_lng
    return [mg_lng, mg_lat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02 (Mars coordinate system) WGS84
    :param lng:Mars lng
    :param lat:Mars lat
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    d_lat = _trans_form_lat(lng - 105.0, lat - 35.0)
    d_lng = _trans_form_lng(lng - 105.0, lat - 35.0)
    rad_lat = lat / 180.0 * pi
    magic = math.sin(rad_lat)
    magic = 1 - ee * magic * magic
    sqrt_magic = math.sqrt(magic)
    d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * pi)
    d_lng = (d_lng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * pi)
    mg_lat = lat + d_lat
    mg_lng = lng + d_lng
    return [lng * 2 - mg_lng, lat * 2 - mg_lat]


def bd09_to_wgs84(bd_lng, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lng, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lng, lat):
    lng, lat = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(lng, lat)


def _trans_form_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _trans_form_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    Whether or not it is in China
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 < 135.05 and 3.86 < lat < 53.55)


def conversion(coordinate_sys, lng, lat):
    lng = float(lng)
    lat = float(lat)
    if coordinate_sys.lower() == 'gcj02':
        # [mg_lng, mg_lat]
        coo = wgs84_to_gcj02(lng, lat)
        return str(coo[0]), str(coo[1])
    if coordinate_sys.lower() == 'bd09':
        #  [bd_lng, bd_lat]
        coo = wgs84_to_bd09(lng, lat)
        return str(coo[0]), str(coo[1])
    return str(lng), str(lat)
