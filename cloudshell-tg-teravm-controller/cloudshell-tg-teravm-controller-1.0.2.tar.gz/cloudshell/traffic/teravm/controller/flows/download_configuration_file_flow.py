import httplib
import os
import tempfile
import urllib
import ftplib

from cloudshell.devices.networking_utils import UrlParser
import scp
import paramiko
import pysftp
import requests


class TeraVMDownloadConfigurationFlow(object):
    def __init__(self, logger):
        """

        :param logging.Logger logger:
        """
        self._logger = logger
        self._protocol_handler_map = {
            "http": self._process_http,
            "https": self._process_http,
            "ftp": self._process_ftp,
            "sftp": self._process_sftp,
            "scp": self._process_scp,
        }

    def _process_http(self, file_path):
        """

        :param str file_path: path to the configuration file (https://10.10.10.10/files/config.xml)
        :return:
        """
        err_msg = "Unable to download configuration file '{}' via HTTP(S). See logs for the details".format(file_path)

        try:
            resp = requests.head(file_path)
        except requests.exceptions.ConnectionError:
            self._logger.exception(err_msg)
            raise Exception(err_msg)

        if resp.status_code != httplib.OK:
            self._logger.error("Unable to download configuration file '{}' via HTTP(S). "
                               "Head request returned {} status code".format(file_path, resp.status_code))
            raise Exception(err_msg)

        tmp_file, _ = urllib.urlretrieve(file_path)
        return tmp_file

    def _process_ftp(self, file_path):
        """

        :param str file_path: path to the configuration file (ftp://user:pass@10.10.10.10/home/config.xml)
        :return:
        """
        full_path_dict = UrlParser().parse_url(file_path)
        address = full_path_dict.get(UrlParser.HOSTNAME)
        username = full_path_dict.get(UrlParser.USERNAME)
        password = full_path_dict.get(UrlParser.PASSWORD)
        port = full_path_dict.get(UrlParser.PORT)
        path = full_path_dict.get(UrlParser.PATH)
        filename = full_path_dict.get(UrlParser.FILENAME)
        tmp_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            ftp = ftplib.FTP()
            ftp.connect(host=address, port=port)
            ftp.login(user=username, passwd=password)
            ftp.cwd(path)
            ftp.retrbinary("RETR " + filename, tmp_file.write)
        except:
            err_msg = "Unable to download configuration file '{}' via FTP. See logs for the details".format(file_path)
            self._logger.exception(err_msg)
            raise Exception(err_msg)

        return tmp_file.name

    def _process_sftp(self, file_path):
        """

        :param str file_path: path to the configuration file (sftp://user:pass@10.10.10.10/home/config.xml)
        :return:
        """
        full_path_dict = UrlParser().parse_url(file_path)
        address = full_path_dict.get(UrlParser.HOSTNAME)
        username = full_path_dict.get(UrlParser.USERNAME)
        password = full_path_dict.get(UrlParser.PASSWORD)
        port = full_path_dict.get(UrlParser.PORT) or 22
        path = full_path_dict.get(UrlParser.PATH)
        filename = full_path_dict.get(UrlParser.FILENAME)

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        temp_file_path = tempfile.mktemp()

        path_to_file = os.path.join(path, filename)
        self._logger.info("Trying to get file '{}' using SFTP".format(path_to_file))

        try:
            with pysftp.Connection(host=address,
                                   port=port,
                                   username=username,
                                   password=password,
                                   cnopts=cnopts
                                   ) as sftp:
                sftp.get(remotepath=path_to_file, localpath=temp_file_path)
                sftp.close()
        except:
            err_msg = "Unable to download configuration file '{}' via SFTP. See logs for the details".format(file_path)
            self._logger.exception(err_msg)
            raise Exception(err_msg)

        return temp_file_path

    def _process_scp(self, file_path):
        """

        :param str file_path: path to the configuration file (scp://user:pass@10.10.10.10/home/config.xml)
        :return:
        """
        full_path_dict = UrlParser().parse_url(file_path)
        address = full_path_dict.get(UrlParser.HOSTNAME)
        username = full_path_dict.get(UrlParser.USERNAME)
        password = full_path_dict.get(UrlParser.PASSWORD)
        port = full_path_dict.get(UrlParser.PORT) or 22
        path = full_path_dict.get(UrlParser.PATH)
        filename = full_path_dict.get(UrlParser.FILENAME)
        path_to_file = os.path.join(path, filename)
        temp_file_path = tempfile.mktemp()

        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=address, port=port, username=username, password=password)
            client = scp.SCPClient(client.get_transport())
            client.get(remote_path=path_to_file, local_path=temp_file_path)
        except:
            err_msg = "Unable to download configuration file '{}' via SCP. See logs for the details".format(file_path)
            self._logger.exception(err_msg)
            raise Exception(err_msg)

        return temp_file_path

    def execute_flow(self, file_path):
        """

        :param str file_path: filename or full path to file
        :rtype: str
        """
        full_path_dict = UrlParser().parse_url(file_path)
        self._logger.info("Parsed config file link: {}".format(full_path_dict))

        protocol = full_path_dict.get(UrlParser.SCHEME)
        handler = self._protocol_handler_map.get(protocol)

        if handler is None:
            raise Exception("Unable to download configuration file '{}'. Invalid protocol type '{}'"
                            .format(file_path, protocol))

        return handler(file_path)
