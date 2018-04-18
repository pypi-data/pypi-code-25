# coding: utf-8

"""
    Wavefront Public API

    <p>The Wavefront public API enables you to interact with Wavefront servers using standard web service API tools. You can use the API to automate commonly executed operations such as automatically tagging sources.</p><p>When you make API calls outside the Wavefront API documentation you must add the header \"Authorization: Bearer &lt;&lt;API-TOKEN&gt;&gt;\" to your HTTP requests.</p><p>For legacy versions of the Wavefront API, see the <a href=\"/api-docs/ui/deprecated\">legacy API documentation</a>.</p>

    OpenAPI spec version: v2
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..api_client import ApiClient


class CloudIntegrationApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def create_cloud_integration(self, **kwargs):
        """
        Create a cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_cloud_integration(async=True)
        >>> result = thread.get()

        :param async bool
        :param CloudIntegration body: Example Body:  <pre>{   \"name\":\"CloudWatch integration\",   \"service\":\"CLOUDWATCH\",   \"cloudWatch\":{     \"baseCredentials\":{       \"roleArn\":\"arn:aws:iam::&lt;accountid&gt;:role/&lt;rolename&gt;\",       \"externalId\":\"wave123\"     },     \"metricFilterRegex\":\"^aws.(sqs|ec2|ebs|elb).*$\",     \"pointTagFilterRegex\":\"(region|name)\"   },   \"serviceRefreshRateInMins\":5 }</pre>
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.create_cloud_integration_with_http_info(**kwargs)
        else:
            (data) = self.create_cloud_integration_with_http_info(**kwargs)
            return data

    def create_cloud_integration_with_http_info(self, **kwargs):
        """
        Create a cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.create_cloud_integration_with_http_info(async=True)
        >>> result = thread.get()

        :param async bool
        :param CloudIntegration body: Example Body:  <pre>{   \"name\":\"CloudWatch integration\",   \"service\":\"CLOUDWATCH\",   \"cloudWatch\":{     \"baseCredentials\":{       \"roleArn\":\"arn:aws:iam::&lt;accountid&gt;:role/&lt;rolename&gt;\",       \"externalId\":\"wave123\"     },     \"metricFilterRegex\":\"^aws.(sqs|ec2|ebs|elb).*$\",     \"pointTagFilterRegex\":\"(region|name)\"   },   \"serviceRefreshRateInMins\":5 }</pre>
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']


        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def delete_cloud_integration(self, id, **kwargs):
        """
        Delete a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_cloud_integration(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.delete_cloud_integration_with_http_info(id, **kwargs)
        else:
            (data) = self.delete_cloud_integration_with_http_info(id, **kwargs)
            return data

    def delete_cloud_integration_with_http_info(self, id, **kwargs):
        """
        Delete a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.delete_cloud_integration_with_http_info(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `delete_cloud_integration`")


        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration/{id}', 'DELETE',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def disable_cloud_integration(self, id, **kwargs):
        """
        Disable a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.disable_cloud_integration(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.disable_cloud_integration_with_http_info(id, **kwargs)
        else:
            (data) = self.disable_cloud_integration_with_http_info(id, **kwargs)
            return data

    def disable_cloud_integration_with_http_info(self, id, **kwargs):
        """
        Disable a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.disable_cloud_integration_with_http_info(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method disable_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `disable_cloud_integration`")


        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration/{id}/disable', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def enable_cloud_integration(self, id, **kwargs):
        """
        Enable a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.enable_cloud_integration(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.enable_cloud_integration_with_http_info(id, **kwargs)
        else:
            (data) = self.enable_cloud_integration_with_http_info(id, **kwargs)
            return data

    def enable_cloud_integration_with_http_info(self, id, **kwargs):
        """
        Enable a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.enable_cloud_integration_with_http_info(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method enable_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `enable_cloud_integration`")


        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration/{id}/enable', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def get_all_cloud_integration(self, **kwargs):
        """
        Get all cloud integrations for a customer
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_all_cloud_integration(async=True)
        >>> result = thread.get()

        :param async bool
        :param int offset:
        :param int limit:
        :return: ResponseContainerPagedCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.get_all_cloud_integration_with_http_info(**kwargs)
        else:
            (data) = self.get_all_cloud_integration_with_http_info(**kwargs)
            return data

    def get_all_cloud_integration_with_http_info(self, **kwargs):
        """
        Get all cloud integrations for a customer
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_all_cloud_integration_with_http_info(async=True)
        >>> result = thread.get()

        :param async bool
        :param int offset:
        :param int limit:
        :return: ResponseContainerPagedCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['offset', 'limit']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_all_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']


        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in params:
            query_params.append(('offset', params['offset']))
        if 'limit' in params:
            query_params.append(('limit', params['limit']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerPagedCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def get_cloud_integration(self, id, **kwargs):
        """
        Get a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_cloud_integration(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.get_cloud_integration_with_http_info(id, **kwargs)
        else:
            (data) = self.get_cloud_integration_with_http_info(id, **kwargs)
            return data

    def get_cloud_integration_with_http_info(self, id, **kwargs):
        """
        Get a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.get_cloud_integration_with_http_info(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `get_cloud_integration`")


        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration/{id}', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def undelete_cloud_integration(self, id, **kwargs):
        """
        Undelete a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.undelete_cloud_integration(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.undelete_cloud_integration_with_http_info(id, **kwargs)
        else:
            (data) = self.undelete_cloud_integration_with_http_info(id, **kwargs)
            return data

    def undelete_cloud_integration_with_http_info(self, id, **kwargs):
        """
        Undelete a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.undelete_cloud_integration_with_http_info(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method undelete_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `undelete_cloud_integration`")


        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration/{id}/undelete', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def update_cloud_integration(self, id, **kwargs):
        """
        Update a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.update_cloud_integration(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :param CloudIntegration body: Example Body:  <pre>{   \"name\":\"CloudWatch integration\",   \"service\":\"CLOUDWATCH\",   \"cloudWatch\":{     \"baseCredentials\":{       \"roleArn\":\"arn:aws:iam::&lt;accountid&gt;:role/&lt;rolename&gt;\",       \"externalId\":\"wave123\"     },     \"metricFilterRegex\":\"^aws.(sqs|ec2|ebs|elb).*$\",     \"pointTagFilterRegex\":\"(region|name)\"   },   \"serviceRefreshRateInMins\":5 }</pre>
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async'):
            return self.update_cloud_integration_with_http_info(id, **kwargs)
        else:
            (data) = self.update_cloud_integration_with_http_info(id, **kwargs)
            return data

    def update_cloud_integration_with_http_info(self, id, **kwargs):
        """
        Update a specific cloud integration
        
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async=True
        >>> thread = api.update_cloud_integration_with_http_info(id, async=True)
        >>> result = thread.get()

        :param async bool
        :param str id: (required)
        :param CloudIntegration body: Example Body:  <pre>{   \"name\":\"CloudWatch integration\",   \"service\":\"CLOUDWATCH\",   \"cloudWatch\":{     \"baseCredentials\":{       \"roleArn\":\"arn:aws:iam::&lt;accountid&gt;:role/&lt;rolename&gt;\",       \"externalId\":\"wave123\"     },     \"metricFilterRegex\":\"^aws.(sqs|ec2|ebs|elb).*$\",     \"pointTagFilterRegex\":\"(region|name)\"   },   \"serviceRefreshRateInMins\":5 }</pre>
        :return: ResponseContainerCloudIntegration
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'body']
        all_params.append('async')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method update_cloud_integration" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `update_cloud_integration`")


        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['api_key']

        return self.api_client.call_api('/api/v2/cloudintegration/{id}', 'PUT',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='ResponseContainerCloudIntegration',
                                        auth_settings=auth_settings,
                                        async=params.get('async'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
