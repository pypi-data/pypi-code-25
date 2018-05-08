#! python
import logging
import os.path
import sys
import traceback
import toil.config
import toil.parm
import toil.parm.parse
import toil.framework
import toil.util.decorator
from toil.batch.base import BaseBatch

logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)


class Batch(BaseBatch):
    def create_toil(self):
        # require a config file to be passed in as parameter
        args = toil.parm.parse.handle_parms(optional=['create', 'create_key', 'encrypt', 'decrypt', 'init'])

        # require config file, encyyption key and initialization vector
        # args = parm.handle.handle_parms(['c', 'k', 'i'])

        logger.debug(args)
        return toil.framework.create(**args)

    @toil.util.decorator.timeit(loops=1)
    def execute(self, framework):
        logger.info('execute')

        logger.debug(framework.args)

        performed_config = False

        if framework.args['init'] is not None:
            self.toil_init(framework, framework.args['init'])
            performed_config = True

        if framework.args['create'] is not None:
            self.create_config(framework, framework.args['create'])
            performed_config = True

        if framework.args['create_key'] is not None:
            self.create_encryption_key(framework, framework.args['create_key'])
            performed_config = True

        if framework.args['encrypt'] is not None:
            self.encrypt(framework, framework.args['encrypt'])
            performed_config = True

        if framework.args['decrypt'] is not None:
            self.decrypt(framework, framework.args['decrypt'])
            performed_config = True

        if not performed_config:
            usage = """
            usage: toil-config [--init CONFIG_DIR_NAME] 
                                    create directory, create config.json, create key
                                    
                                  [--create FILE_NAME]
                                    create config file with file name
                                    
                                  [--create_key FILE_NAME]
                                    create encryption key with file name
                                    
                                  [--encrypt CONFIG_FILE_NAME]
                                    encrypt config file
                                     
                                  [--decrypt CONFIG_FILE_NAME]
                                    decrypt config file 
                                  
            To get started try this:
            
                toil-config --init /path/.toil
                    creates a config.json file in your directory and an encryption key
                    
                toil-config -k /path/.toil/key --encrypt /path/.toil/config.json
                    create the file /path/.toil/config.json.encrypted where all values are encrypted
                    
                toil-config -k /path/.toil/key --decrypt /Users/aclove/.toil/config.json.encrypted
                    create the file /path/.toil/config.json.encrypted.decrypted where all values are decrypted
                    
            """
            print(usage)

    def toil_init(self, framework, dir_name):
        self.create_config(framework, dir_name + '/config.json')

        self.create_encryption_key(framework, dir_name + '/key')

    def create_config(self, framework, file_name):
        try:
            if os.path.isfile(file_name):
                print('The file {0} already exists'.format(file_name))
            else:
                toil.config.util.generate_config_file(file_name)
                print('created {0}'.format(file_name))

        except Exception as ex:
            logger.error(ex)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.error(message)
            traceback.print_exc(file=sys.stdout)

    def create_encryption_key(self, framework, file_name):
        try:
            if os.path.isfile(file_name):
                print('The file {0} already exists'.format(file_name))
            else:
                key = framework.encryptor.generate_key(file_name)
                print('created {0} with value {1}'.format(file_name, key))

        except Exception as ex:
            logger.error(ex)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.error(message)
            traceback.print_exc(file=sys.stdout)

    def encrypt(self, framework, file_name):
        logger.info('execute')

        try:
            framework.encrypt_config_file(file_name, file_name + '.encrypted')

        except Exception as ex:
            logger.error(ex)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.error(message)
            traceback.print_exc(file=sys.stdout)

    def decrypt(self, framework, file_name):
        logger.info('execute')

        try:
            framework.decrypt_config_file(file_name, file_name + '.decrypted')

        except Exception as ex:
            logger.error(ex)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.error(message)
            traceback.print_exc(file=sys.stdout)

def main():
    Batch().run()
