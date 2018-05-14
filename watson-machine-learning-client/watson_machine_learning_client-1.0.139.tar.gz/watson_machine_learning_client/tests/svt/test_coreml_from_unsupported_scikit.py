import unittest
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import WMLClientError
from preparation_and_cleaning import *
from watson_machine_learning_client.utils import delete_directory
from models_preparation import *
from sys import platform
from sklearn.externals import joblib

class TestWMLClientWithScikit2CoreML(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    converted_model_path = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithScikit2CoreML.logger.info("Service Instance: setting up credentials")
        self.wml_credentials = get_wml_credentials()
        self.client = get_client()
        #self.model_path = os.path.join(os.getcwd(), 'artifacts', 'core_ml', 'sklearn', 'iris_svc_with_pca.pkl')

    def test_01_service_instance_details(self):
        TestWMLClientWithScikit2CoreML.logger.info("Check client ...")
        self.assertTrue(self.client.__class__.__name__ == 'WatsonMachineLearningAPIClient')

        self.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithScikit2CoreML.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_publish_model(self):
        TestWMLClientWithScikit2CoreML.logger.info("Creating scikit-learn model ...")

        model_data = create_scikit_learn_model_data('iris')
        predicted = model_data['prediction']

        TestWMLClientWithScikit2CoreML.logger.debug(predicted)
        self.assertIsNotNone(predicted)

        self.logger.info("Publishing scikit-learn model ...")

        self.client.repository.ModelMetaNames.show()

        model_props = {
                        self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                        self.client.repository.ModelMetaNames.NAME: "Iris Species prediction",
                      }

        published_model_details = self.client.repository.store_model(model=model_data['model'], meta_props=model_props, training_data=model_data['training_data'], training_target=model_data['training_target'])
        TestWMLClientWithScikit2CoreML.model_uid = self.client.repository.get_model_uid(published_model_details)
        self.logger.info("Published model ID:" + str(TestWMLClientWithScikit2CoreML.model_uid))
        self.assertIsNotNone(TestWMLClientWithScikit2CoreML.model_uid)

    def test_04_publish_model_details(self):
        details_models = self.client.repository.get_model_details()
        TestWMLClientWithScikit2CoreML.logger.debug("All models details: " + str(details_models))
        self.assertTrue("Iris Species prediction" in str(details_models))

    def test_05_convert_2_coreml(self):
        self.logger.info("Try converting scikit-learn model to core ml ...")

        self.assertRaises(WMLClientError, self.client.deployments._create_virtual, TestWMLClientWithScikit2CoreML.model_uid)
        #self.logger.info("Converted file location: " + str(TestWMLClientWithScikit2CoreML.converted_model_path))
        #self.assertTrue('.mlmodel' in str(TestWMLClientWithScikit2CoreML.converted_model_path))

    # def test_06_load_CoreML_model(self):
    #     # Load the model
    #     import coremltools
    #     loaded_model = coremltools.models.MLModel(TestWMLClientWithScikit2CoreML.converted_model_path)
    #     loaded_model.short_description = 'this is a test model'
    #     self.assertTrue('this is a test model' in str(loaded_model.short_description))
    #
    #     if not platform in ['linux']:
    #         scoring_data = {'input': [0.0, 0.0, 5.0, 16.0, 16.0, 3.0, 0.0, 0.0, 0.0, 0.0, 9.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 15.0,
    #                                   2.0, 0.0, 0.0, 0.0, 0.0, 1.0, 15.0, 16.0, 15.0, 4.0, 0.0, 0.0, 0.0, 0.0, 9.0, 13.0, 16.0, 9.0, 0.0, 0.0,
    #                                   0.0, 0.0, 0.0, 0.0, 14.0, 12.0, 0.0, 0.0, 0.0, 0.0, 5.0, 12.0, 16.0, 8.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.0,
    #                                   15.0, 1.0, 0.0, 0.0]}
    #
    #         predictions = loaded_model.predict(scoring_data)
    #         self.assertTrue('5' in str(predictions))

    def test_10_delete_model(self):
        delete_directory(TestWMLClientWithScikit2CoreML.model_uid)
        self.client.repository.delete(TestWMLClientWithScikit2CoreML.model_uid)

if __name__ == '__main__':
    unittest.main()
