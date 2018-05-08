################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
from watson_machine_learning_client.href_definitions import HrefDefinitions
from watson_machine_learning_client.utils import delete_directory, get_model_filename, install_package
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.log_util import get_logger
import os
install_package('coremltools')
import coremltools
import tarfile
import requests
from repository_v3.mlrepositoryclient import MLRepositoryClient


class ModelConverter:
    """
        Converts model to different type.
    """
    def __init__(self, service_path, instance_id, token):
        self.target_filename = 'model.mlmodel'
        self.token = token
        self._logger = get_logger(__name__)
        self.service_path = service_path
        self.instance_id = instance_id
        self._repo_client = MLRepositoryClient(self.service_path)
        self._repo_client.authorize_with_token(token)
        self._href_definitions = HrefDefinitions({
            'url': self.service_path,
            'instance_id': self.instance_id
        })

    def _get_model_details(self, model_uid):
        response = requests.get(
            self._href_definitions.get_published_model_href(model_uid),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.token,
                'X-WML-User-Client': 'PythonClient'
            }
        )

        if response.status_code is not 200:
            raise Exception('Error while getting model details: ' + response.text)

        return response.json()

    def _load_model(self, model_uid):
        return self._repo_client.models.get(model_uid).model_instance()

    def _extract_model_from_repository(self, model_uid):
        delete_directory(model_uid)
        os.makedirs(model_uid)
        current_dir = os.getcwd()

        os.chdir(model_uid)
        model_dir = os.getcwd()

        fname = 'downloaded_' + model_uid + '.tar.gz'

        if os.path.isfile(fname):
            raise Exception(u'File with name: \'{}\' already exists.'.format(fname))

        artifact_url = self._href_definitions.get_model_last_version_href(model_uid)

        import requests

        try:
            artifact_content_url = str(artifact_url + '/content')
            r = requests.get(artifact_content_url, headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.token,
                'X-WML-User-Client': 'PythonClient'
            }, stream=True)
            downloaded_model = r.content
            self._logger.info(u'Successfully downloaded artifact with artifact_url: {}'.format(artifact_url))
        except Exception as e:
            raise WMLClientError(u'Downloading model with artifact_url: \'{}\' failed.'.format(artifact_url), e)

        try:
            with open(fname, 'wb') as f:
                f.write(downloaded_model)
            self._logger.info(u'Successfully saved artifact to file: \'{}\''.format(fname))
        except IOError as e:
            raise WMLClientError(u'Saving model with artifact_url: \'{}\' failed.'.format(fname), e)

        tar = tarfile.open(fname)
        tar.extractall()
        tar.close()

        os.chdir(current_dir)
        return model_dir

    def run(self, model_uid, file_format='core ml', meta_props=None):
        model_details = self._get_model_details(model_uid)
        framework = model_details['entity']['model_type']
        short_description = model_details['entity']['name']
        filepath = None

        print(u'Model conversion started ...')

        if 'core ml' in file_format:
            if 'scikit' in framework:
                filepath = self.scikit_to_coreml(model_uid, meta_props, short_description)
            elif 'tensorflow' in framework:
                filepath = self.keras_to_coreml(model_uid, meta_props, short_description)
            elif 'xgboost' in framework:
                filepath = self.xgboost_to_coreml(model_uid, meta_props, short_description)
            elif 'caffe' in framework:
                filepath = self.caffe_to_coreml(model_uid, meta_props, short_description)
        else:
            raise WMLClientError(u'Incorrect file format. "core ml" file format is only supported.')

        return filepath

    def keras_to_coreml(self, model_uid, meta_props=None, short_description=''):
        model_dir = self._extract_model_from_repository(model_uid)
        model_extension = 'h5'
        model_filename = get_model_filename(model_dir, model_extension)

        print(u'Keras ' + model_uid + ' conversion in progress ...')

        if meta_props is None:
            meta_props = {}

        try:
            coreml_model = coremltools.converters.keras.convert(model_filename, **meta_props)
            print(u'Keras ' + model_uid + ' conversion completed.')
            coreml_model.short_description = short_description
            target_path = os.path.join(model_uid, self.target_filename)
            coreml_model.save(target_path)
            filepath = os.path.abspath(target_path)
            print(u'Core ML model stored: ' + str(filepath))
        except ValueError as e:
            raise WMLClientError(u'Failed during conversion model: \'{}\'.'.format(model_uid), e)

        return filepath

    def scikit_to_coreml(self, model_uid, meta_props=None, short_description=''):
        model = self._load_model(model_uid)

        print(u'Scikit ' + model_uid + ' conversion in progress ...')

        if meta_props is None:
            meta_props = {}

        try:
            coreml_model = coremltools.converters.sklearn.convert(model, **meta_props)
            coreml_model.short_description = short_description
            delete_directory(model_uid)
            os.makedirs(model_uid)
            target_path = os.path.join(model_uid, self.target_filename)
            coreml_model.save(target_path)
            filepath = os.path.abspath(target_path)
            print(u'Core ML model stored: ' + str(filepath))
        except ValueError as e:
            raise WMLClientError(u'Failed during conversion model: \'{}\'.'.format(model_uid), e)

        return filepath

    def xgboost_to_coreml(self, model_uid, meta_props=None, short_description=''):
        model = self._load_model(model_uid)

        print(u'Caffe ' + model_uid + ' conversion in progress ...')

        if meta_props is None:
            meta_props = {}

        try:
            coreml_model = coremltools.converters.caffe.convert(model, **meta_props)
            coreml_model.short_description = short_description
            delete_directory(model_uid)
            os.makedirs(model_uid)
            target_path = os.path.join(model_uid, self.target_filename)
            coreml_model.save(target_path)
            filepath = os.path.abspath(target_path)
            print(u'Core ML model stored: ' + str(filepath))
        except ValueError as e:
            raise WMLClientError(u'Failed during conversion model: \'{}\'.'.format(model_uid), e)

        return filepath

    def caffe_to_coreml(self, model_uid, meta_props=None, short_description=''):
        model_dir = self._extract_model_from_repository(model_uid)
        model_extension = 'caffemodel'
        proto_extension = 'json'
        model_filename = get_model_filename(model_dir, model_extension)
        prototxt_filename = get_model_filename(model_dir, proto_extension)

        print(u'Caffe ' + model_uid + ' conversion in progress ...')

        if meta_props is None:
            meta_props = {}

        try:
            coreml_model = coremltools.converters.caffe.convert(model_filename, prototxt_filename, **meta_props)
            print(u'Caffe ' + model_uid + ' conversion completed.')
            coreml_model.short_description = short_description
            target_path = os.path.join(model_uid, self.target_filename)
            coreml_model.save(target_path)
            filepath = os.path.abspath(target_path)
            print(u'Core ML model stored: ' + str(filepath))
        except ValueError as e:
            raise WMLClientError(u'Failed during conversion model: \'{}\'.'.format(model_uid), e)

        return filepath

