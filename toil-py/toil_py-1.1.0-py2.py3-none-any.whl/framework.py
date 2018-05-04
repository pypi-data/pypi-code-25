# -*- coding: utf-8 -*-
"""
Toil Library
  Author: Andrew Love
  Provides a library of code for interacting with cloud technology such as OCI, AWS, OPENSTACK, SCALR and CHEF.
"""
import json
import provider.datasource
import crypto.symmetric
import config.util
import logging
import glob
import os.path
import re
import sys
import importlib
import codecs

logger = logging.getLogger(__name__)


def create(env=None, config_json=None, config_file=None, encryption_key=None, encryption_iv=None,
           encrypted_config_keys_regex=None, **args):
    """
    Load the toil library based on the configuration provided.  All sensitive keys in the config file are expected
    to be encrypted.  Any config keys named with a match to encrypted_config_keys_regex parameter
    are automatically decrypted/encrypted.

    Args:
      env (str): the environment such as preprod, stage, prod, etc.
      config_json (str): the configuration may be passed as a json string
      config_file (str): the configuration file
      encryption_key (str): the key used for encryption and decryption
      encryption_iv (str): the initialization vector for encryption
      encrypted_config_keys_regex (): all keys in config file matching are encrypted and decrypted
      **args ():

    Returns:
      Toil.ToilLib
    """
    logger.debug("config_file={config_file}".format(config_file=config_file))
    logger.debug("config_json={config_json}".format(config_json=config_json))

    map = {}
    if config_file is not None:
        with open(config_file) as json_data:
            map = json.load(json_data)
    elif config_json is not None:
        map = json.loads(config_json)

    if env in map:
        config = map[env]
    elif len(map) > 0:
        # since env is not in0 config, grab the first one available
        config = map.values().pop()
    else:
        config = {}
    # no environment defined

    toil = ToilLib(config, env, encryption_key, encryption_iv, encrypted_config_keys_regex, **args)

    return toil


class ToilLib:
    """
    Main class for the cloud framework.
    """

    @property
    def args(self):
        return self._env

    @args.setter
    def args(self, value):
        self._env = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, value):
        self._env = value

    @property
    def encryption_key(self):
        return self._encryption_key

    @encryption_key.setter
    def encryption_key(self, value):
        self._encryption_key = value

    @property
    def encryption_iv(self):
        return self._encryption_iv

    @encryption_iv.setter
    def encryption_iv(self, value):
        self._encryption_iv = value

    @property
    def encrypted_config_keys_regex(self):
        return self._encrypted_config_keys_regex

    @encrypted_config_keys_regex.setter
    def encrypted_config_keys_regex(self, value):
        self._encrypted_config_keys_regex = value

    @property
    def encryptor(self):
        return self._encryptor

    @encryptor.setter
    def encryptor(self, value):
        self._encryptor = value

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, value):
        self._datasource = value

    def __init__(self, config, env, encryption_key, encryption_iv, encrypted_config_keys_regex, **args):
        """
        Initializes the library.

        Args:
          env (): the environment such as preprod, stage, prod, etc.
          config (): dict with configuration data
          encryption_key (): the key used for encryption and decryption
          encryption_iv (): the initialization vector for encryption
          **args ():

        Returns:
          Nothing
        """
        self._config = None
        self._datasource = None
        self._encryptor = None
        self._encrypted_config_keys_regex = None
        self._encryption_key = None
        self._encryption_iv = None
        self._env = None
        self._services = None

        self.config = config
        self.env = env
        self.encryption_key = encryption_key
        self.encryption_iv = encryption_iv
        self.encrypted_config_keys_regex = encrypted_config_keys_regex
        self.args = args
        self._services = {}

        self.init_crypto()
        self.init_datasources()
        self.init_services()

    def init_services(self):
        """
        Initializes services from the config. Each service becomes an attribute of this class.
        Config uses the alias if defined otherwise service name.
        i.e. you can call toil.myservice.some_method()

        args:
          self ():


        returns: Nothing
        """
        # dynamically load services defined in config
        # if 'services' in self.config.get(self.env, {}):
        if 'services' in self.config:
            service_config = self.config['services']

            for service, service_config_values in service_config.items():
                logger.debug("loading service:{service}".format(service=service))

                try:
                    if 'alias' in service_config_values:
                        service_attribute_mapping = service_config_values['alias']
                    else:
                        service_attribute_mapping = service

                    if service_attribute_mapping in dir(self):
                        message = "service name:{service_name} conflicts with existing attribute. {attributes}".format(
                            service_name=service_attribute_mapping, attributes=dir(self))
                        message += "set the alias property for {service_name} in config file to change the attribute mapping" \
                            .format(service_name=service_attribute_mapping)
                        raise CloudException(message)

                    # provider_class_name = service_config_values['provider']
                    provider_class_name = service_config_values['provider']
                    logger.debug(
                        "service provider:{provider_class_name}".format(provider_class_name=provider_class_name))
                    provider_class = self.load_class(provider_class_name)
                    # create an instance of the service
                    self._services[service_attribute_mapping] = provider_class(self, service_config_values)
                    # map an attribute to the service alias.  i.e. you can call toil.myservice.some_method()
                    set_service_property_exec = \
                        "self.__class__.{service_name} = property(lambda self: self._services['{service_name}'])" \
                            .format(service_name=service_attribute_mapping)
                    # set_service_property_exec = "self.{service_name} = self._services['{service_name}']".format(
                    # service_name=service_attribute_mapping)
                    logger.debug(set_service_property_exec)
                    exec set_service_property_exec
                except CloudClassLoadException as ex:  # catch *all* exceptions
                    logger.error(
                        "unable to load service provider: {provider_class_name}".format(
                            provider_class_name=provider_class_name))
                    logger.error(ex)

    def init_datasources(self):
        """
        Instantiate and initialize DatasourceLib with configuration data.

        Returns:
          Nothing
        """

        ds_config = {}
        if 'datasources' in self.config:
            ds_config = self.config['datasources']

        self.datasource = provider.datasource.DatasourceLib(self, ds_config)

    def init_crypto(self):
        """
        Instantiate and initialize encryption with configuration data.

        Returns:
          Nothing
        """
        crypt_config = {}
        if 'crypto' in self.config.get('services', {}):
            crypt_config = self.config['services']['crypto']

        self.encryptor = crypto.symmetric.SymmetricEncryptor(crypt_config)

        if self.encryption_key is not None:
            self.encryptor.encryption_key = self.encryption_key
            self.encryptor.encryption_iv = self.encryption_iv
            self.traverse_config(self.decrypt_config_item, self.config)

    def traverse_config(self, handler, root, node=None, path='', **args):
        """
        Recursively visit each item in a a dict.

        Args:
          handler (): a function to run on each node
          root (): the root node
          node (): the node to process
          path (): the path to node

        Returns:
          Nothing
        """
        if node is None:
            node = root

        for k, v in node.iteritems():
            if isinstance(v, dict):
                if len(path) > 0:
                    self.traverse_config(handler, root, v, "{0}['{1}']".format(path, k), **args)
                else:
                    self.traverse_config(handler, root, v, "['{0}']".format(k), **args)
            else:
                handler(root, "{0}['{1}']".format(path, k), v, **args)

    def decrypt_config_item(self, root, key, value, **args):
        """
        Decrypt a configuration item.

        Args:
          root(): the root of dict
          key (): the dict key
          value (): the current node value

        Returns:

        """
        # if re.search( r'key_id|secret|password',key ):
        if re.search(self.encrypted_config_keys_regex, key):
            try:
                logger.debug("attempting to decrypt " + key)
                confidential_data = self.encryptor.decrypt(value, **args).strip()
                # set the value in dictionary
                # eval_set_string =  "self.config{0} = \"{1}\"".format(key , confidential_data)
                eval_set_string = "root{0} = \"{1}\"".format(key, confidential_data)
                # logger.debug(eval_set_string)
                exec eval_set_string
            except:  # catch *all* exceptions
                logger.debug("unable to decrypt " + key)
                # e = sys.exc_info()[0]
                # logger.error("error in decrypt_config_item " + key + ":" + str(e))

    def encrypt_config_item(self, root, key, value, **args):
        """
        Encrypt a configuration item.

        Args:
          key (): the dict key
          value (): the current node value

        Returns:

        """
        if re.search(self.encrypted_config_keys_regex, key):
            try:
                if isinstance(value, basestring):
                    encrypted_data = self.encryptor.encrypt(value, **args).strip()
                    # set the value in dictionary
                    # eval_set_string =  "self.config{0} = \"{1}\"".format(key , encrypted_data)
                    eval_set_string = "root{0} = \"{1}\"".format(key, encrypted_data)
                    logger.debug(eval_set_string)
                    exec eval_set_string
            except:  # catch *all* exceptions
                e = sys.exc_info()[0]
                logger.error("error in encrypt_config_item " + key + ":" + str(e))

    def traverse_dir(self, path, handler, original_path=None, level=1, **kwargs):
        """
        Walk through a directory structure

        Args:
          path (): the path to walk
          handler (): a function to call for each file
          original_path ():
          level ():
          **kwargs ():

        Returns:
          Nothing
        """
        if os.path.isfile(path):
            file_path, filename = os.path.split(path)
            handler(path, file_path, filename, **kwargs)
        else:
            for i in glob.glob(os.path.join(path, "*")):
                if os.path.isfile(i):
                    file_path, filename = os.path.split(i)
                    handler(i, file_path, filename, **kwargs)
                    # print '----' *c + filename + ' ' + os.path.relpath(filepath, '/')
                elif os.path.isdir(i):
                    # dirname = os.path.basename(i)
                    # print '----' *c + dirname
                    level += 1
                    self.traverse_dir(i, handler, original_path, level, **kwargs)
                    level -= 1

    def load_class(self, full_class_string):
        """
        Dynamically load a class from a string

        Args:
          full_class_string (): the class to load

        Returns:
          Class
        """
        try:
            class_data = full_class_string.split(".")
            module_path = ".".join(class_data[:-1])
            class_str = class_data[-1]

            # Finally, we retrieve the Class
            if module_path == "":
                return getattr(globals(), class_str)
            else:
                module = importlib.import_module(module_path)
                return getattr(module, class_str)
        except Exception as ex:
            raise CloudClassLoadException(ex)

    def generate_config_file(self, file_name=None):
        return config.util.generate_config_file(file_name)

    def encrypt_config_file(self, file_name_in, file_name_out, **args):
        logger.info('encrypt config file')
        logger.info('config file confidential:{file_name}'.format(file_name=file_name_in))
        logger.info('config file encrypted:{file_name}'.format(file_name=file_name_out))
        with codecs.open(file_name_in) as json_data:
            temp_config = json.load(json_data)

        self.traverse_config(self.encrypt_config_item, temp_config, **args)

        with codecs.open(file_name_out, 'w', 'utf-8') as f:
            f.write(json.dumps(temp_config, sort_keys=True, indent=4, separators=(',', ': ')))
            f.write('\n')

    def decrypt_config_file(self, file_name_in, file_name_out, **args):
        logger.info('decrypt config file')
        logger.info('config file encrypted:{file_name}'.format(file_name=file_name_in))
        logger.info('config file confidential:{file_name}'.format(file_name=file_name_out))
        with codecs.open(file_name_in) as json_data:
            temp_config = json.load(json_data)

        self.traverse_config(self.decrypt_config_item, temp_config, **args)

        with codecs.open(file_name_out, 'w', 'utf-8') as f:
            f.write(json.dumps(temp_config, sort_keys=True, indent=4, separators=(',', ': ')))
            f.write('\n')


class BaseCloudException(Exception):
    """ root for exceptions, only used to except any Package error, never raised"""
    pass


class CloudException(BaseCloudException):
    """
    Default exception used in the framework.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CloudClassLoadException(CloudException):
    """
    Default exception used in the framework.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
