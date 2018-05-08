# -*- coding: utf-8 -*-
"""
Provide a wrapper and helpers for OCI library.
See https://pypi.python.org/pypi/openstacksdk for API details

"""
from __future__ import absolute_import

import logging

import enum
import oci

import toil.provider.base
from toil.framework import CloudException

logger = logging.getLogger(__name__)


class OciSdkLib(toil.provider.base.BaseProvider):
    """
    library for OCI functionality.
    """

    def __init__(self, toils, config):
        super(OciSdkLib, self).__init__(toils, config)

    def session(self, profile='default'):
        """
        Create an OCI session.

        Args:
          profile (): the profile defined in config to use

        Returns:
          3.session.Session
        """
        if profile in self.config:
            self.configure_proxy()
            # create a session
            return OciSession(self._toil, profile, self.config[profile])
        else:
            raise CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


@enum.unique
class OciServiceType(enum.Enum):
    AUDIT = "audit"
    BLOCK_STORAGE = "blockstorage"
    COMPUTE = "compute"
    VIRTUAL_NETWORK = "virtualnetwork"
    DATABASE = "database"
    DNS = "dns"
    EMAIL = "email"
    FILE_STORAGE = "filestorage"
    IDENTITY = "identity"
    LOAD_BALANCER = "loadbalancer"
    OBJECT_STORAGE = "objectstorage"

#session object for the oci library
class OciSession(object):
    """
    provide open stack api access
    """

    def __init__(self, toils, profile, config):
        self._profile = profile
        self._config = config
        self._toil = toils

    # provide and validate the config
    def oci_config(self):

        config = {
            "user": self._config["user_ocid"],
            "key_file": self._config["key_file"],
            "fingerprint": self._config["fingerprint"],
            "tenancy": self._config["tenancy"],
            "region": self._config["region"],
            "log_requests":
                (self._config["log_requests"] if "log_requests" in self._config.keys() else False)
        }

        from oci.config import validate_config
        validate_config(config)

        return config

    def config(self):
        return self._config

    # page through response
    def paginate(self, operation, *args, **kwargs):
        while True:
            response = operation(*args, **kwargs)
            for value in response.data:
                yield value
            kwargs["page"] = response.next_page
            if not response.has_next_page:
                break

    #construct an appropriate oci client
    def client(self, service, **kwargs):

        try:
            service_type = OciServiceType(service)

        except Exception as ex:
            logger.error(ex)
            raise CloudException(
                "client '{service}' not supported".format(service=service))

        clients = {"audit": oci.audit.AuditClient,
                  "blockstorage": oci.core.BlockstorageClient,
                   "compute": oci.core.compute_client.ComputeClient,
                   "virtualnetwork": oci.core.VirtualNetworkClient,
                   "database": oci.database.DatabaseClient,
                   "dns": oci.dns.DnsClient,
                   "email": oci.email.EmailClient,
                   "filestorage": oci.file_storage.FileStorageClient,
                   "identity": oci.identity.identity_client.IdentityClient,
                   "loadbalancer": oci.load_balancer.LoadBalancerClient,
                   "objectstorage": oci.object_storage.ObjectStorageClient
                   }

        return clients[service_type.value] (self.oci_config(), **kwargs)

    # check if the ocid that was provided is valid
    def check_instance_ocid(self, p_compute_client, p_instance_id):
        try:
            get_instance_response = p_compute_client.get_instance(instance_id=p_instance_id)
        except oci.exceptions.ServiceError:
            return (False)

        #if not get_instance_response.data.shape.startswith('VM.Standard'):
        #    return False

        return (True)

    # get information regarding the source instance
    def get_instance_info(self, p_compute_client, p_virtual_network_client, p_instance_id):
        get_instance_response = p_compute_client.get_instance(instance_id=p_instance_id)
        l_inst_name = get_instance_response.data.display_name
        l_ad = get_instance_response.data.availability_domain
        l_compartment_id = get_instance_response.data.compartment_id
        l_image_id = get_instance_response.data.image_id
        l_shape = get_instance_response.data.shape
        l_boot_volume_id = self.get_boot_volume_id(p_compute_client, l_ad, l_compartment_id, p_instance_id)
        l_subnet_id = self.get_subnet_id(p_compute_client, p_virtual_network_client, l_compartment_id, p_instance_id)
        return ({"instance_name": l_inst_name, "availability_domain": l_ad, "compartment_id": l_compartment_id
            , "image_id": l_image_id, "shape": l_shape, "boot_volume_id": l_boot_volume_id, "subnet_id": l_subnet_id})

    # get attached volumes
    def get_block_volumes(self, p_compute_client, p_compartment_id, p_instance_id):
        l_bv_list = []
        get_block_volume_response = p_compute_client.list_volume_attachments(p_compartment_id,
                                                                             instance_id=p_instance_id)
        for rec in get_block_volume_response.data:
            if rec.lifecycle_state == 'ATTACHED':
                l_bv_list.append({"vol_attach_id": rec.id, "vol_id": rec.volume_id, "display_name": rec.display_name})
        return l_bv_list

    # get the boot volume id
    def get_boot_volume_id(self, p_compute_client, p_ad, p_compartment_id, p_instance_id):
        list_boot_volume_response = p_compute_client.list_boot_volume_attachments(p_ad, p_compartment_id,
                                                                                instance_id=p_instance_id)
        return (list_boot_volume_response.data[0].boot_volume_id)

    # get the subnet id
    def get_subnet_id(self, p_compute_client, p_virtual_network_client, p_compartment_id, p_instance_id):
        list_vnics_response = p_compute_client.list_vnic_attachments(compartment_id=p_compartment_id,
                                                                     instance_id=p_instance_id)
        list_vnic_det = p_virtual_network_client.get_vnic(vnic_id=list_vnics_response.data[0].vnic_id)
        return (list_vnic_det.data.subnet_id)

    # detach a list of block volumes
    def detach_block_volumes(self, p_compute_client, p_block_volume_list):
        for rec in p_block_volume_list:
            p_compute_client.detach_volume(rec['vol_attach_id'])
            oci.wait_until(
                p_compute_client,
                p_compute_client.get_volume_attachment(rec['vol_attach_id']),
                'lifecycle_state',
                'DETACHED',
                succeed_on_not_found=True
            )

    # terminate the instance and wait till it is terminated
    def terminate_instance(self, p_compute_client, p_instance_id):
        p_compute_client.terminate_instance(instance_id=p_instance_id, preserve_boot_volume=True)
        oci.wait_until(
            p_compute_client,
            p_compute_client.get_instance(p_instance_id),
            'lifecycle_state',
            'TERMINATED',
            succeed_on_not_found=True
        )

    # stop the instance and wait till it is terminated
    def stop_instance(self, p_compute_client, p_instance_id):
        p_compute_client.instance_action(instance_id=p_instance_id, action='STOP')
        oci.wait_until(
            p_compute_client,
            p_compute_client.get_instance(p_instance_id),
            'lifecycle_state',
            'STOPPED',
            succeed_on_not_found=True
        )

    # create the instance and wait till it is created
    def create_instance(self, p_compute_client, p_instance_info, p_target_shape):
        launch_instance_details = oci.core.models.LaunchInstanceDetails(
            display_name=p_instance_info['instance_name'],
            compartment_id=p_instance_info['compartment_id'],
            availability_domain=p_instance_info['availability_domain'],
            shape=p_target_shape,
            source_details=oci.core.models.InstanceSourceViaBootVolumeDetails(
                boot_volume_id=p_instance_info['boot_volume_id']),
            create_vnic_details=oci.core.models.CreateVnicDetails(
                subnet_id=p_instance_info['subnet_id']
            )
        )
        launch_instance_response = p_compute_client.launch_instance(launch_instance_details)
        oci.wait_until(
            p_compute_client,
            p_compute_client.get_instance(launch_instance_response.data.id),
            'lifecycle_state',
            'RUNNING'
        )
        return launch_instance_response.data.id

    # attach a list of block volumes
    def attach_block_volumes(self, p_compute_client, p_block_volume_list, p_instance_id):
        for rec in p_block_volume_list:
            block_volume_details = oci.core.models.AttachVolumeDetails(
                display_name=rec['display_name'],
                instance_id=p_instance_id,
                is_read_only=False,
                type='iscsi',
                volume_id=rec['vol_id']
            )
            block_volume_attach_response = p_compute_client.attach_volume(block_volume_details)
            oci.wait_until(
                p_compute_client,
                p_compute_client.get_volume_attachment(block_volume_attach_response.data.id),
                'lifecycle_state',
                'ATTACHED',
            )

    # vertically scale instace (change shape) terminates instance so be careful
    def scale_vertical(self, p_compute_client, p_virtual_network_client, p_instance_id, p_target_shape):
        if not self.check_instance_ocid(p_compute_client, p_instance_id):
            raise CloudException(
                "instance ocid '{instance_id}' was not found".format(instance_id=p_instance_id))

        if p_compute_client is None:
            p_compute_client = self.client("compute")

        if p_virtual_network_client is None:
            p_virtual_network_client = self.client("virtualnetwork")

        logging.info('vertical scale begin')

        # Get information regarding the source instance
        d_instance_info = self.get_instance_info(p_compute_client, p_virtual_network_client, p_instance_id)
        l_block_volume_list = self.get_block_volumes(p_compute_client, d_instance_info['compartment_id'], p_instance_id)

        if len(l_block_volume_list) > 0:
            logging.info('Detaching block volumes: {volumes}'.format(volumes=l_block_volume_list))
            self.detach_block_volumes(p_compute_client, l_block_volume_list)

        # Terminate the instance
        logging.info('Terminating  instance: {instance_id}'.format(instance_id=p_instance_id))
        self.terminate_instance(p_compute_client, p_instance_id)

        # Create the instance
        logging.info('Creating instance')
        l_new_instance_id = self.create_instance(p_compute_client, d_instance_info, p_target_shape)

        if len(l_block_volume_list) > 0:
            logging.info('Attaching block volumes')
            self.attach_block_volumes(p_compute_client, l_block_volume_list, l_new_instance_id)

        logging.info('vertical scale complete')
