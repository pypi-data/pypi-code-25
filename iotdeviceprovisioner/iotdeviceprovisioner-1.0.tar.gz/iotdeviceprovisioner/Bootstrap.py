
import os
import errno
import json
import datetime
import logging
import subprocess
import botocore.auth
from botocore.exceptions import ClientError
import iotbotocredentialprovider.AWS


log = logging.getLogger()
log.setLevel(logging.INFO)


default_thing_group_name = "MyIoTThings"
default_thing_type_name = "MyIoTThingv1"
default_role_alias_name = "MyIoTThingv1"
default_policy_name = "MyIoTThingPolicy"
default_stack_name = "iotdevices-iam-base"


class BaseManagementClass(object):
    def __init__(self, **kwargs):
        self.boto3_session = kwargs.get("boto3_session", None)

        if self.boto3_session is None:
            raise ValueError("a boto3 session must be provided")

    @property
    def region(self):
        return self.boto3_session.region_name

    @property
    def account_id(self):
        return self.sts_client.get_caller_identity()['Account']

    @property
    def sts_client(self):
        if not hasattr(self, "_sts_client"):
            self._sts_client = self.boto3_session.client('sts')
        return self._sts_client

    @property
    def iot_client(self):
        if not hasattr(self, "_iot_client"):
            self._iot_client = self.boto3_session.client('iot')
        return self._iot_client

    @property
    def cf_client(self):
        if not hasattr(self, "_cf_client"):
            self._cf_client = self.boto3_session.client('cloudformation')
        return self._cf_client


class InitialAccountRegionSetup(BaseManagementClass):
    """
    This configures an account/region for
    provisioning devices to use iotbotocredentialprovider.
    Once done we will be able to provision
    devices in the account.

    Note: this requires that a cloudformation stack named
    iotdevices-iam-base will have been created
    ahead of time via the template included with this package

    to use:

    import boto3.session
    from iotdeviceprovisioner import InitialAccountRegionSetup

    region = "us-east-2"  # change this as appropriate
    boto3_session = boto3.session.Session(region_name=region)

    i = InitialAccountRegionSetup(boto3_session=boto3_session)
    i.provision_region()
    """

    def __init__(self, **kwargs):
        super(InitialAccountRegionSetup, self).__init__(**kwargs)

        self.stack_name = kwargs.get("stack_name", default_stack_name)
        self.role_alias_name = kwargs.get("role_alias_name", default_role_alias_name)
        self.policy_name = kwargs.get("policy_name", default_policy_name)
        self.thing_type_name = kwargs.get("thing_type_name", default_thing_type_name)
        self.thing_group_name = kwargs.get("thing_group_name", default_thing_group_name)

    def get_stack_metadata(self):
        stack = self.cf_client.describe_stacks(StackName=self.stack_name)['Stacks'][0]
        stack_outputs = {output['OutputKey']: output['OutputValue'] for output in stack['Outputs']}
        self._role_devices_get_arn = stack_outputs['DeviceInitialRole']

    @property
    def role_devices_get_arn(self):
        if not hasattr(self, "_role_devices_get_arn"):
            self.get_stack_metadata()
        return self._role_devices_get_arn

    @property
    def policy_doc(self):
        return """{
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "*",
              "Resource": "*"
            }
          ]
        }"""

    def create_role_alias(self):
        try:
            output = self.iot_client.create_role_alias(roleAlias=self.role_alias_name,
                                                       roleArn=self.role_devices_get_arn)
            self.role_alias_arn = output['roleAliasArn']
            logging.info("created role alias")
        except ClientError as e:
            if not e.response['Error']['Code'] == "ResourceAlreadyExistsException":
                raise

    def create_group_policy(self):
        try:
            self.iot_client.create_policy(policyName=self.policy_name,
                                          policyDocument=self.policy_doc)
            logging.info("created group policy")
        except ClientError as e:
            if not e.response['Error']['Code'] == "ResourceAlreadyExistsException":
                raise

    def create_group(self):
        self.create_group_policy()

        try:
            o = self.iot_client.create_thing_group(thingGroupName=self.thing_group_name)
            logging.info("created thing group")
            self.thing_group_arn = o['thingGroupArn']
            self.iot_client.attach_policy(policyName=self.policy_name,
                                          target=self.thing_group_arn)
            logging.info("attached group policy")
        except ClientError as e:
            if not e.response['Error']['Code'] == "ResourceAlreadyExistsException":
                raise

    def create_type(self):
        try:
            self.iot_client.create_thing_type(thingTypeName=self.thing_type_name)
            logging.info("created thing type")
        except ClientError as e:
            if not e.response['Error']['Code'] == "ResourceAlreadyExistsException":
                raise

    def provision_region(self):
        self.create_type()
        self.create_group()
        self.create_role_alias()


class DeviceProvisioner(BaseManagementClass):
    """
    This provisions a device in IoT and creates appropriate
    local metadata files, allowing us to obtain
    certificates/keys which can be traded for temporary AWS credentials.

    To use:

    import boto3.session
    from iotdeviceprovisioner import DeviceProvisioner

    region = "us-east-2"  # change as appropriate
    boto3_session = boto3.session.Session(region_name=region)
    s = DeviceProvisioner("devicename", "beta", "/path/to/data",
                         boto3_session=boto3_session)
    s.provision_device()
    """

    def __init__(self, device_name,
                 stage,
                 output_file_path,
                 **kwargs):

        super(DeviceProvisioner, self).__init__(**kwargs)

        self.stage = stage
        self.device_name = device_name
        self.output_file_path = output_file_path

        self.thing_group = kwargs.get("thing_group", default_thing_group_name)
        self.thing_type = kwargs.get("thing_type", default_thing_type_name)
        self.role_alias_name = kwargs.get("role_alias_name", default_role_alias_name)
        self.allow_rotate = kwargs.get("allow_rotate", False)

        self.metadata_filename = os.path.join(output_file_path, "metadata.json")
        self.metadata_save_filename = self.metadata_filename + "." + datetime.datetime.utcnow().strftime("%s")

    def get_thing(self):
        try:
            self.thing = self.iot_client.describe_thing(thingName=self.device_name)
            return self.thing
        except ClientError:
            return None

    def create_thing(self):
        self.thing = self.iot_client.create_thing(thingName=self.device_name,
                                                  thingTypeName=self.thing_type)

        logging.info("created device %s", self.thing["thingName"])

    def add_thing_to_group(self):
        self.iot_client.add_thing_to_thing_group(thingName=self.thing['thingName'],
                                                 thingGroupName=self.thing_group)
        logging.info("added device to group %s", self.thing_group)

    def create_certificate(self):
        self.cert_response = self.iot_client.create_keys_and_certificate(setAsActive=True)
        self.short_certificate_id = self.cert_response['certificateId'][0:17]
        logging.info("created certificate")

    def write_certificate_files(self):
        pem_file = os.path.join(self.output_file_path, "%s.pem" % self.short_certificate_id)
        private_key_file = os.path.join(self.output_file_path, "%s.privatekey") % self.short_certificate_id
        public_key_file = os.path.join(self.output_file_path, "%s.publickey" % self.short_certificate_id)

        if not os.path.isdir(self.output_file_path):
            try:
                os.makedirs(self.output_file_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        with open(pem_file, "w") as f:
            f.write(self.cert_response["certificatePem"])
            logging.info("wrote pem to %s", pem_file)

        with open(private_key_file, "w") as f:
            f.write(self.cert_response["keyPair"]["PrivateKey"])
            os.chmod(private_key_file, 0o600)
            logging.info("wrote private key to %s", private_key_file)

        with open(public_key_file, "w") as f:
            f.write(self.cert_response["keyPair"]["PublicKey"])
            logging.info("wrote public key to %s", public_key_file)

    def delete_old_certificate_files(self, short_certificate_id):
        if short_certificate_id == self.short_certificate_id:
            raise RuntimeError("not deleting currently active certificate")

        pem_file = os.path.join(self.output_file_path, "%s.pem" % short_certificate_id)
        private_key_file = os.path.join(self.output_file_path, "%s.privatekey") % short_certificate_id
        public_key_file = os.path.join(self.output_file_path, "%s.publickey" % short_certificate_id)

        os.unlink(pem_file)
        os.unlink(private_key_file)
        os.unlink(public_key_file)
        logging.info("deleted certificate files for %s", short_certificate_id)

    def attach_certificate(self):
        self.iot_client.attach_thing_principal(thingName=self.thing['thingName'],
                                               principal=self.cert_response['certificateArn'])
        logging.info("attached certificate %s to %s",
                     self.short_certificate_id,
                     self.thing['thingName'])

    def get_certificate_info(self, certificate_id=None):
        if certificate_id is None:
            certificate_id = self.cert_response['certificateId']

        return self.iot_client.describe_certificate(certificateId=certificate_id)['certificateDescription']

    @property
    def credential_endpoint(self):
        if not hasattr(self, "_credential_endpoint"):
            o = self.iot_client.describe_endpoint(endpointType="iot:CredentialProvider")
            _credential_endpoint = "https://" + o['endpointAddress']
        return _credential_endpoint

    def get_nvram_data(self, data_type):
        data = {}
        if not os.path.exists("/usr/bin/dmidecode"):
            return data

        cmd = [
            "/usr/sbin/dmidecode",
            "-q",
            "-t",
            data_type
        ]
        dmidecode = subprocess.Popen(cmd,
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)
        output, error = dmidecode.communicate()

        lines = output.split("\n")
        for line in lines[1:]:
            if line:
                k, v = line.strip().split(":")
                data[k.strip()] = v.strip()
        return data

    def get_all_nvram_data(self):
        data = {}
        if not os.path.exists("/usr/bin/dmidecode"):
            return data

        data_types = ["chassis", "system"]
        for data_type in data_types:
            data[data_type] = (self.get_nvram_data(data_type))
        return data

    @property
    def metadata(self):
        if not hasattr(self, "_metadata"):
            self._metadata = {
                "account_id": self.account_id,
                "stage": self.stage,
                "region": self.region,
                "device_name": self.device_name,
                "thing_arn": self.thing['thingArn'],
                "credential_endpoint": self.credential_endpoint,
                "certificate_id": self.short_certificate_id,
                "full_certificate_id": self.cert_response['certificateId'],
                "certificate_arn": self.cert_response['certificateArn'],
                "certificate_creation_date": self.get_certificate_info()['creationDate'].strftime(botocore.auth.ISO8601),
                "role_alias_name": self.role_alias_name,
                "nvram_data": self.get_all_nvram_data(),
            }
        return self._metadata

    def write_metadata(self):
        with open(self.metadata_filename, "w") as f:
            json.dump(self.metadata, f, sort_keys=True, indent=4)
            logging.info("wrote metadata")

    def save_metadata(self):
        if os.path.exists(self.metadata_filename):
            os.rename(self.metadata_filename, self.metadata_save_filename)
            logging.info("saved metadata to %s", self.metadata_save_filename)

    def revert_metadata(self):
        os.rename(self.metadata_save_filename, self.metadata_filename)
        logging.info("put old metadata back in place")

    def delete_old_metadata(self):
        if os.path.exists(self.metadata_save_filename):
            os.unlink(self.metadata_save_filename)
            logging.info("deleted old metadata file")

    def get_metadata(self, filename=None):
        if filename is None:
            filename = self.metadata_filename

        try:
            return json.load(open(filename))
        except ValueError:
            return {}
        except IOError as e:
            # ignore file not found
            if e.errno == 2:
                return {}
            raise e

    def validate_new_certificate(self):
        old_metadata = self.get_metadata(filename=self.metadata_save_filename)
        metadata = self.get_metadata()

        # make sure that the new certificate is different than the old one
        if old_metadata.get("certificate_id") == metadata.get("certificate_id"):
            raise RuntimeError("New certificate appears to be the same as the old certificate")

        # make sure we can obtain credentials with the new certificate
        cp = iotbotocredentialprovider.AWS.IotBotoCredentialProvider()

        try:
            creds = cp.get_credentials()
        except Exception:
            return False

        required_fields = ['secretAccessKey', 'sessionToken', 'expiration', 'accessKeyId']
        for field in required_fields:
            if field not in creds:
                logging.info("new certificate validation failed")
                return False

        logging.info("validated new certificate")
        return True

    def delete_old_certificate(self):
        old_metadata = self.get_metadata(filename=self.metadata_save_filename)
        certificate_id = old_metadata.get("full_certificate_id")

        if certificate_id:
            short_certificate_id = certificate_id[0:17]
            certificate_arn = old_metadata.get("certificate_arn")

            self.iot_client.detach_thing_principal(thingName=self.thing["thingName"],
                                                   principal=certificate_arn)
            logging.info("detached certificate %s from %s", short_certificate_id, self.thing["thingName"])

            self.iot_client.update_certificate(certificateId=certificate_id,
                                               newStatus='INACTIVE')
            logging.info("deactivated certificate %s", short_certificate_id)

            self.iot_client.delete_certificate(certificateId=certificate_id)
            logging.info("deleted certificate %s", short_certificate_id)

            self.delete_old_certificate_files(short_certificate_id)

        self.delete_old_metadata()

    def rotate_device_certificate(self):
        self.create_certificate()
        self.attach_certificate()
        self.write_certificate_files()
        self.save_metadata()
        self.write_metadata()

        if not self.validate_new_certificate():
            self.revert_metadata()
            raise RuntimeError("New certificate failed validation, reverted to old one")

        self.delete_old_certificate()

    def provision_device(self):
        metadata = self.get_metadata()
        if metadata:
            if metadata.get("device_name", self.device_name) != self.device_name:
                raise RuntimeError("Attempt to provision device as %s, but it is already provisioned as %s",
                                   self.device_name,
                                   metadata.get("device_name"))

            if metadata.get("account_id", self.account_id) != self.account_id:
                raise RuntimeError("Attempt to provision device in account %s, but it is already provisioned in %s",
                                   self.account_id,
                                   metadata.get("account_id"))

            if metadata.get("region", self.region) != self.region:
                raise RuntimeError("Attempt to provision device in region %s, but it is already provisioned in %s",
                                   self.region,
                                   metadata.get("region"))

        if self.get_thing():
            if not self.allow_rotate:
                raise RuntimeError("A device named %s is already provisioned" % self.device_name)
            return self.rotate_device_certificate()

        self.create_thing()
        self.add_thing_to_group()
        self.create_certificate()
        self.attach_certificate()
        self.write_certificate_files()
        self.write_metadata()


def provision_device(device_name, stage, boto3_session,
                     allow_rotate=True,
                     directory=iotbotocredentialprovider.AWS.default_iot_metadata_path):
    s = DeviceProvisioner(device_name,
                          stage,
                          output_file_path=directory,
                          allow_rotate=allow_rotate,
                          boto3_session=boto3_session)

    s.provision_device()

    print("This device has been provisioned/updated with an IoT certificate in %s of %s" % (s.region, s.account_id))


def configure_account_region(boto3_session):
    i = InitialAccountRegionSetup(boto3_session=boto3_session)
    i.provision_region()

    print("Configured %s in account %s" % (i.region, i.account_id))
