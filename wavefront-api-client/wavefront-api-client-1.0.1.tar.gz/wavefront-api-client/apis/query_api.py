# coding: utf-8

"""
QueryApi.py
Copyright 2016 SmartBear Software

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from __future__ import absolute_import

import sys
import os

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient


class QueryApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client

    def chart(self, q, s, g, **kwargs):
        """
        Perform a charting query against Wavefront servers which returns the appropriate points in the specified time window and granularity
        Be aware that long time spans and small granularities can take a long time to calculate

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.chart(q, s, g, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str q: the query expression to execute (required)
        :param str s: the start time of the query window (required)
        :param str g: the granularity of the points returned (required)
        :param str n: name used to identify the query
        :param str e: the end time of the query window (null to use now)
        :param str p: the maximum number of points to return
        :param bool i: whether series with only points that are outside of the query window will be returned (defaults to true)
        :param bool auto_events: whether events for sources included in the query will be automatically returned by the query
        :param str summarization: summarization strategy to use when bucketing points together
        :param bool list_mode: retrieve events more optimally displayed for a list
        :param bool strict: do not return points outside the query window [q;s), defaults to false
        :param bool include_obsolete_metrics: include metrics that have not been reporting recently, defaults to false
        :param bool sorted: sorts the output so that returned series are in order, defaults to false
        :return: QueryResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['q', 's', 'g', 'n', 'e', 'p', 'i', 'auto_events', 'summarization', 'list_mode', 'strict', 'include_obsolete_metrics', 'sorted']
        all_params.append('callback')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method chart" % key
                )
            params[key] = val
        del params['kwargs']

        # verify the required parameter 'q' is set
        if ('q' not in params) or (params['q'] is None):
            raise ValueError("Missing the required parameter `q` when calling `chart`")
        # verify the required parameter 's' is set
        if ('s' not in params) or (params['s'] is None):
            raise ValueError("Missing the required parameter `s` when calling `chart`")
        # verify the required parameter 'g' is set
        if ('g' not in params) or (params['g'] is None):
            raise ValueError("Missing the required parameter `g` when calling `chart`")

        resource_path = '/chart/api'.replace('{format}', 'json')
        path_params = {}

        query_params = {}
        if 'n' in params:
            query_params['n'] = params['n']
        if 'q' in params:
            query_params['q'] = params['q']
        if 's' in params:
            query_params['s'] = params['s']
        if 'e' in params:
            query_params['e'] = params['e']
        if 'g' in params:
            query_params['g'] = params['g']
        if 'p' in params:
            query_params['p'] = params['p']
        if 'i' in params:
            query_params['i'] = params['i']
        if 'auto_events' in params:
            query_params['autoEvents'] = params['auto_events']
        if 'summarization' in params:
            query_params['summarization'] = params['summarization']
        if 'list_mode' in params:
            query_params['listMode'] = params['list_mode']
        if 'strict' in params:
            query_params['strict'] = params['strict']
        if 'include_obsolete_metrics' in params:
            query_params['includeObsoleteMetrics'] = params['include_obsolete_metrics']
        if 'sorted' in params:
            query_params['sorted'] = params['sorted']

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json', 'application/x-javascript; charset&#x3D;UTF-8', 'application/javascript; charset&#x3D;UTF-8'])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, 'GET',
                                            path_params,
                                            query_params,
                                            header_params,
                                            body=body_params,
                                            post_params=form_params,
                                            files=local_var_files,
                                            response_type='QueryResult',
                                            auth_settings=auth_settings,
                                            callback=params.get('callback'))
        return response

    def raw_query(self, metric, **kwargs):
        """
        Perform a raw data query against Wavefront servers which returns second granularity points grouped by tags
        User can use this API to check if ingested points are as expected. Note that points ingested within a single second are averaged when returned.

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.raw_query(metric, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str metric: metric to query ingested points for (cannot contain wildcards) (required)
        :param str host: host to query ingested points for (cannot contain wildcards). host or source is equivalent, only one should be used.
        :param str source: source to query ingested points for (cannot contain wildcards). host or source is equivalent, only one should be used.
        :param int start_time: start time in milliseconds (cannot be more than a day in the past) null to use an hour before endTime
        :param int end_time: end time in milliseconds (cannot be more than a day in the past) null to use now
        :return: list[Timeseries]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['metric', 'host', 'source', 'start_time', 'end_time']
        all_params.append('callback')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method raw_query" % key
                )
            params[key] = val
        del params['kwargs']

        # verify the required parameter 'metric' is set
        if ('metric' not in params) or (params['metric'] is None):
            raise ValueError("Missing the required parameter `metric` when calling `raw_query`")

        resource_path = '/chart/raw'.replace('{format}', 'json')
        path_params = {}

        query_params = {}
        if 'host' in params:
            query_params['host'] = params['host']
        if 'source' in params:
            query_params['source'] = params['source']
        if 'metric' in params:
            query_params['metric'] = params['metric']
        if 'start_time' in params:
            query_params['startTime'] = params['start_time']
        if 'end_time' in params:
            query_params['endTime'] = params['end_time']

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None

        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])
        if not header_params['Accept']:
            del header_params['Accept']

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type([])

        # Authentication setting
        auth_settings = ['api_key']

        response = self.api_client.call_api(resource_path, 'GET',
                                            path_params,
                                            query_params,
                                            header_params,
                                            body=body_params,
                                            post_params=form_params,
                                            files=local_var_files,
                                            response_type='list[Timeseries]',
                                            auth_settings=auth_settings,
                                            callback=params.get('callback'))
        return response
