from cloudshell.traffic.teravm.cli.ctrl_handler import TeraVMControllerCliHandler

from cloudshell.traffic.teravm.controller.flows.load_configuration_file_flow import TeraVMLoadConfigurationFlow
from cloudshell.traffic.teravm.controller.flows.download_configuration_file_flow import TeraVMDownloadConfigurationFlow


class TeraVMLoadConfigurationRunner(object):
    def __init__(self, cli, cs_api, resource_config, reservation_id, logger):
        """

        :param cloudshell.cli.cli.CLI cli: CLI object
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cs_api: cloudshell API object
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param str reservation_id:
        :param logging.Logger logger:
        """
        self._cli = cli
        self._cs_api = cs_api
        self._resource_config = resource_config
        self._reservation_id = reservation_id
        self._logger = logger

    @property
    def cli_handler(self):
        """

        :rtype: TeraVMControllerCliHandler
        """
        return TeraVMControllerCliHandler(self._cli,
                                          self._resource_config,
                                          self._logger,
                                          self._cs_api)

    @property
    def upload_configuration_flow(self):
        """Upload configuration file to the controller

        :rtype: TeraVMLoadConfigurationFlow
        """
        return TeraVMLoadConfigurationFlow(cli_handler=self.cli_handler,
                                           resource_config=self._resource_config,
                                           reservation_id=self._reservation_id,
                                           cs_api=self._cs_api,
                                           logger=self._logger)

    @property
    def download_configuration_flow(self):
        """Download config file from the FTP|SFTP|HTTP server and save to the temp directory

        :rtype: TeraVMLoadConfigurationFlow
        """
        return TeraVMDownloadConfigurationFlow(logger=self._logger)

    def load_configuration(self, test_file_path, use_ports_from_reservation):
        """

        :param str test_file_path:
        :param bool use_ports_from_reservation:
        """
        config_file = self.download_configuration_flow.execute_flow(file_path=test_file_path)
        self._logger.info("Downloaded Config file: {}".format(config_file))

        return self.upload_configuration_flow.execute_flow(file_path=config_file,
                                                           use_ports_from_reservation=use_ports_from_reservation)
