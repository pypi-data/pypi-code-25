# -*- coding: utf-8 -*-l
# Copyright (c) 2017 Vantiv eCommerce
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
from __future__ import absolute_import, print_function, unicode_literals

import mimetypes
import re

import requests
from requests.auth import HTTPBasicAuth

from cnpsdk import (utils)

conf = utils.Configuration()

CHARGEBACK_API_HEADERS = {"Accept": "application/com.vantivcnp.services-v2+xml",
                          "Content-Type": "application/com.vantivcnp.services-v2+xml"}

HTTP_ERROR_MESSAGE = "Error with Https Request, Please Check Proxy and Url configuration"


def http_get_retrieval_request(request_url, config=conf):
    try:
        http_response = requests.get(request_url, headers=CHARGEBACK_API_HEADERS,
                                     auth=HTTPBasicAuth(config.username, config.password))

    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nGET request to:", request_url, config)
    check_response(http_response)
    print_to_console("\nResponse :", http_response.text, config)
    return utils.generate_retrieval_response(http_response)


def http_put_request(request_url, request_xml, config=conf):
    request_xml = utils.obj_to_xml(request_xml)
    try:
        http_response = requests.put(request_url, headers=CHARGEBACK_API_HEADERS,
                                     auth=HTTPBasicAuth(config.username, config.password),
                                     data=request_xml)
    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nPUT request to:", request_url, config)
    print_to_console("\nRequest :", request_xml, config)
    check_response(http_response)
    print_to_console("\nResponse :", http_response.text, config)
    return utils.generate_update_response(http_response)
    

def http_get_document_request(request_url, document_path, config=conf):
    try:
        http_response = requests.get(request_url, auth=HTTPBasicAuth(config.username, config.password))

    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nGET Request to:", request_url, config)
    check_response(http_response)
    retrieve_file(http_response, document_path, config)


def http_delete_document_response(request_url, config=conf):
    try:
        http_response = requests.delete(request_url, auth=HTTPBasicAuth(config.username, config.password))

    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nDELETE request to:", request_url, config)
    check_response(http_response)
    print_to_console("\nResponse :", http_response.text, config)
    return utils.generate_document_response(http_response)
    

def http_post_document_request(request_url, document_path, config=conf):
    try:
        data, content_type = get_file_content(document_path)
        http_response = requests.post(url=request_url,
                                      headers={"Content-Type": content_type},
                                      auth=HTTPBasicAuth(config.username, config.password), data=data)
    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nPOST request to:", request_url, config)
    print_to_console("\nFile:", document_path, config)
    check_response(http_response)
    print_to_console("\nResponse :", http_response.text, config)
    return utils.generate_document_response(http_response)
    

def http_put_document_request(request_url, document_path, config=conf):
    try:
        data, content_type = get_file_content(document_path)
        http_response = requests.put(url=request_url,
                                     headers={"Content-Type": content_type},
                                     auth=HTTPBasicAuth(config.username, config.password), data=data)
    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nPUT request to:", request_url, config)
    print_to_console("\nFile:", document_path, config)
    check_response(http_response)
    print_to_console("\nResponse :", http_response.text, config)
    return utils.generate_document_response(http_response)
    

def http_get_document_list_request(request_url, config=conf):
    try:
        http_response = requests.get(request_url, headers=CHARGEBACK_API_HEADERS,
                                     auth=HTTPBasicAuth(config.username, config.password))

    except requests.RequestException:
        raise utils.VantivException(HTTP_ERROR_MESSAGE)

    print_to_console("\nGET request to:", request_url, config)
    check_response(http_response)
    print_to_console("\nResponse :", http_response.text, config)
    return utils.generate_document_response(http_response)
    

def check_response(http_response, config=conf):
    """check the status code of the response
    :param http_response: http response generated
    :return: raises an exception
    """

    if http_response.status_code != 200:
        error_response = utils.generate_error_response(http_response)
        print_to_console("\nResponse :", http_response.text, config)
        raise utils.VantivException(str(http_response.status_code) + " : " + str(http_response.reason) + " - " + str(error_response['errors']['error']))

    # Check empty response
    if not http_response:
        raise utils.VantivException("The response is empty, Please call Vantiv eCommerce")


def retrieve_file(http_response, document_path, config=conf):
    content_type = http_response.headers._store['content-type'][1]
    if content_type != "image/tiff":
        error_response = utils.generate_error_response(http_response)
        print_to_console("\nResponse :", http_response.text, config)
        raise utils.VantivException(str(error_response['errors']['error']))
    else:
        with open(document_path, 'wb') as f:
            for block in http_response.iter_content(1024):
                f.write(block)
        print_to_console("\nDocument saved at: ", document_path, config)


def get_file_content(path):
    with open(path, 'rb') as f:
        data = f.read()
    content_type = mimetypes.guess_type(path)[0]
    return data, content_type


def neuter_xml(xml_string):
    xml_string = re.sub(r"<accNum>.*</accNum>", "<accNum>****</accNum>", xml_string)
    xml_string = re.sub(r"<user>.*</user>", "<user>****</user>", xml_string)
    xml_string = re.sub(r"<password>.*</password>", "<password>****</password>", xml_string)
    xml_string = re.sub(r"<track>.*</track>", "<track>****</track>", xml_string)
    xml_string = re.sub(r"<number>.*</number>", "<number>****</number>", xml_string)
    return xml_string


def print_to_console(prefix_message, xml_string, config=conf):
    if config.print_xml:
        if config.neuter_xml:
            xml_string = neuter_xml(xml_string)
        print(prefix_message, xml_string)
