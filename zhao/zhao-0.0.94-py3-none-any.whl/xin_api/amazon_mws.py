#!/usr/bin/env python3
# -*- coding:utf-8 -*-
""" Amazon MWS API
"""

__author__ = "Zhao Xin <7176466@qq.com>"
__license__ = "GNU General Public License v3 (GPLv3)"
__version__ = "2018-05-14"

import os
import time
import hmac
import base64
import hashlib
from urllib.parse import urlencode, quote
import requests
import xmltodict

# 从环境参数读取信息
_AWS_DEVELOPER_ID = os.environ.get("AWS_DEVELOPER_ID", "")
_AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
_AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
_MWS_SELLER_ID = os.environ.get("MWS_SELLER_ID", "")
_MWS_AUTH_TOKEN = os.environ.get("MWS_AUTH_TOKEN", "")

_SESSION = requests.Session()


def _create_mws_api_request_signature(host, path, parameters, aws_secret_key=_AWS_SECRET_KEY):
    """返回 Amazon MWS API 请求签名
    创建该请求签名需要将 host, path, parameters 格式化为 http 请求字符串，
    并用 aws_secret_key 作为密钥求该请求字符串的 HMACSHA256 散列值，
    该散列值经 base64 编码即为所需的请求签名。
    """
    # 请求参数 parameters 必须按键名排序
    # 并用 urllib.parse.urlencode 以 utf-8 编码 及 urllib.parse.quote 函数处理
    parameters_string = urlencode(query=sorted(parameters.items()), encoding="utf-8", quote_via=quote)
    http_request_message = "POST\n%s\n%s\n%s" % (host, path, parameters_string)
    hmacsha256_hash = hmac.new(key=aws_secret_key.encode("utf-8"),
                               msg=http_request_message.encode("utf-8"),
                               digestmod=hashlib.sha256)
    signature = base64.b64encode(hmacsha256_hash.digest())
    return signature


def mws_get_matching_products(asins: list):
    """ Amazon MWS API - GetMatchingProduct """

    base_request_parameters = {
        'AWSAccessKeyId':   _AWS_ACCESS_KEY_ID,
        'MWSAuthToken':	    _MWS_AUTH_TOKEN,
        'SellerId':         _MWS_SELLER_ID,
        'MarketplaceId':    'ATVPDKIKX0DER',  # US MARKETPLACE ID
        'SignatureMethod':  'HmacSHA256',
        'SignatureVersion': '2',
        'Action':	        'GetMatchingProduct',
        'Version':	        '2011-10-01'
    }

    asins = list(asins)
    while asins:
        # build request parameters (10 asins max per request)
        parameters = base_request_parameters.copy()
        parameters.update({'ASINList.ASIN.%d' % (i+1): asin for i, asin in enumerate(asins[:10])})

        while True:
            parameters['Timestamp'] = time.strftime(r'%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            parameters['Signature'] = _create_mws_api_request_signature(host='mws.amazonservices.com',
                                                                        path='/Products/2011-10-01',
                                                                        parameters=parameters)
            try:
                response = _SESSION.post(url='https://mws.amazonservices.com/Products/2011-10-01',
                                         data=parameters,
                                         timeout=(3.0, 5.0))
                assert 'text/xml' in response.headers.get('Content-Type')
                asins = asins[10:]
                break
            except (requests.exceptions.RequestException, AssertionError):
                continue
            except KeyboardInterrupt:
                exit(0)

        dom = xmltodict.parse(response.content).get('GetMatchingProductResponse', {})
        matched_products = dom.get('GetMatchingProductResult', [])
        if not isinstance(matched_products, list):
            matched_products = [matched_products, ]

        for product in matched_products:
            if product.get('@status') == 'ClientError':
                product_info = {}
            elif product.get('@status') == 'Success':
                asin = product['@ASIN']
                product = product.get('Product', {})
                attributes = product.get('AttributeSets', {}).get('ns2:ItemAttributes', {})
                dimensions = attributes.get('ns2:ItemDimensions', {})
                pkg_dims = attributes.get('ns2:PackageDimensions', {})

                # SalesRankings
                sales_ranks = product.get('SalesRankings', {})
                if not sales_ranks:
                    sales_ranks = {}
                else:
                    sales_ranks = sales_ranks.get('SalesRank', [])
                    if not isinstance(sales_ranks, list):
                        sales_ranks = dict([sales_ranks.values()])
                    else:
                        sales_ranks = dict(item.values() for item in sales_ranks)
                    # Conver rank from string to int
                    for node, rank in sales_ranks.items():
                        sales_ranks[node] = int(rank)

                # 执行 zhang yiwei 修改材质逻辑
                title = attributes.get('ns2:Title', '')
                material = str(attributes.get('ns2:MaterialType', ''))

                # Build product details information
                product_info = {
                    'date': time.strftime(r'%Y-%m-%d'),
                    'asin': asin,
                    'label': attributes.get('ns2:Label', ''),
                    'title': title,
                    'binding': attributes.get('ns2:Binding', ''),
                    'brand': attributes.get('ns2:Brand', ''),
                    'color': attributes.get('ns2:Color', ''),
                    'manufacturer': attributes.get('ns2:Manufacturer', ''),
                    'material': material,
                    'partnumber': attributes.get('ns2:PartNumber', ''),
                    'productgroup': attributes.get('ns2:ProductGroup', ''),
                    'producproducttypenametgroup': attributes.get('ns2:ProductTypeName', ''),
                    'Publisher': attributes.get('ns2:Publisher', ''),
                    'size': attributes.get('ns2:Size', ''),
                    'studio': attributes.get('ns2:Studio', ''),
                    'model': attributes.get('ns2:Model', ''),
                    'price': float(attributes.get('ns2:ListPrice', {}).get('ns2:Amount', '0.00')),
                    'warranty': attributes.get('ns2:Warranty', ''),
                    'small_image': attributes.get('ns2:SmallImage', {}).get('ns2:URL', ''),
                    'height': float(dimensions.get('ns2:Height', {}).get('#text', '0.00')),
                    'length': float(dimensions.get('ns2:Length', {}).get('#text', '0.00')),
                    'width': float(dimensions.get('ns2:Width', {}).get('#text', '0.00')),
                    'weight': float(dimensions.get('ns2:Weight', {}).get('#text', '0.00')),
                    'package_height': float(pkg_dims.get('ns2:Height', {}).get('#text', '0.00')),
                    'package_length': float(pkg_dims.get('ns2:Length', {}).get('#text', '0.00')),
                    'package_width': float(pkg_dims.get('ns2:Width', {}).get('#text', '0.00')),
                    'package_weight': float(pkg_dims.get('ns2:Weight', {}).get('#text', '0.00')),
                    'sales_ranks': sales_ranks,
                    'quota_remaining': float(response.headers.get('x-mws-quota-remaining', '0.0')),
                }

            else:
                continue

            time.sleep(0.5)
            yield product_info
