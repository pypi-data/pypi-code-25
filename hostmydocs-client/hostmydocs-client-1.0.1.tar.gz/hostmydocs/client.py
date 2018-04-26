#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
from typing import List, Optional

import requests
import urllib.parse

from hostmydocs import ServerConfig, Documentation


class Client:
    """
    This class can be used to communicate with HostMyDocs easily
    """

    def __init__(self, server_config: ServerConfig):
        """

        :param server_config: The configuration for your HostMyDocs instance
        """
        self.server_config = server_config

    def upload_documentation(self, doc: Documentation) -> bool:
        """
        Send the documentation to hostMyDocs server

        :param doc: The documentation you want to store on HostMyDocs server
        :return: True if uploaded with success
        """

        if doc.is_local_documentation() is False:
            logging.error("Impossible to upload not local documentation")
            return False

        request_url = urllib.parse.urljoin(self.server_config.get_server_url(), "/BackEnd/addProject")

        logging.info("Send documentation to HostMyDocs: {}".format(request_url))

        payload = {'name': doc.name, 'language': doc.language, 'version': doc.version}
        logging.debug("Data: {}".format(payload))

        archive_stream = open(doc.zip_archive_path, 'rb')
        files = {'archive': archive_stream}
        headers = {"Authorization": 'Basic {}'.format(self.server_config.get_credential_for_basic_auth())}

        try:
            response = requests.post(request_url, headers=headers, files=files, data=payload, verify=False)
        except Exception as error:
            logging.error("Upload fail with error {}".format(error))
            return False
        finally:
            archive_stream.close()

        if response.status_code == requests.codes.ok:
            logging.info("Uploaded with success")
            return True
        else:
            logging.error("Upload fail with code {}".format(response.status_code))
            return False

    def get_all_documentations(self) -> Optional[List[Documentation]]:
        """
        Get all documentations hosted in the HostMyDocs server

        :return: The list of documentations or None if an error occurred
        """

        request_url = urllib.parse.urljoin(self.server_config.get_server_url(), "/BackEnd/listProjects")
        logging.info("List documentation in HostMyDocs: {}".format(request_url))
        headers = {"Authorization": 'Basic {}'.format(self.server_config.get_credential_for_basic_auth())}

        try:
            response = requests.get(request_url, headers=headers, verify=False)
        except Exception as error:
            logging.error("Listing fail with error {}".format(error))
            return None

        if response.status_code != requests.codes.ok:
            logging.error("Listing fail with code {}".format(response.status_code))
            return None

        logging.debug("List docs done with success")

        list_of_documentation = []
        for project in response.json():
            for version in project["versions"]:
                for language in version["languages"]:
                        list_of_documentation.append(Documentation(
                            name=project['name'],
                            version=version['number'],
                            language=language['name']
                        ))

        return list_of_documentation
