# -*- coding: utf-8 -*-
import json
import os
import random
from ...utils.http_utils import http_request
from requests_toolbelt.multipart.encoder import MultipartEncoder


class File(object):
    @staticmethod
    def _list(auth, path):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/fileservice/v1/file")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        request_body = json.dumps(dict(action="list",
                                       path=path))
        status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _upload(auth, dest, files):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/fileservice/v1/file")
        http_method = "POST"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token}
        file_name = "file"
        body_dict = {}
        for index, _file in enumerate(files):
            if os.access(_file, os.R_OK):
                body_dict["{}-{}".format(file_name, index)] = (os.path.basename(_file), open(_file, 'rb'), 'application/octet-stream')
            else:
                raise Exception("File Error")
        body_dict["destination"] = dest
        multipart_encoder = MultipartEncoder(
            fields=body_dict
        )
        headers['Content-Type'] = multipart_encoder.content_type
        status, response_data = http_request(url=url, http_method=http_method, body=multipart_encoder, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        result = data.get("result",{})
        if result.get("success"):
            print "Uploade files:{} success".format(",".join(files))
        else:
            print result.get("error")

    @staticmethod
    def _download(auth, path):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        filename = os.path.basename(path)
        url = "{}://{}{}?action=download&path={}&Authorization={}&X-Access-Authority={}".format(
            security, address, "/dispatch/fileservice/v1/file", path, auth_token, access_authority_token)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        status, content = http_request(url=url, http_method=http_method, headers=headers)
        if status == 200:
            with open(filename, 'wb') as f:
                f.write(content)
        print "success"
