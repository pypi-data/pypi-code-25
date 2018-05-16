import logging
from path import Path


settings = {'headers': 'period providerRecordId extractDate serviceStartDate serviceEndDate invoiceStartDate invoiceEndDate providerInvoiceId providerFinalBillFlag providerName assetAccountId billingAccountId providerRegion assetName providerAssetId assetParentId description quantity unitOfMeasure providerCurrency pcProviderUnitCost pcProviderTotalCost pcProviderTaxCost pcCustomerUnitCost pcCustomerTotalCost customerCurrency customerConversionRate customerCurrencyDate orderId providerServiceDescription tags assetType', 'dateformat': '%Y-%m-%d %H:%M:%S.%f', 'cost_constants': {'default_unit_cost': 0.0, 'usage_data_duration_type': 2, 'policy_type_compute': 'Compute', 'unit_of_measure_per_vcpu': 'Per vCPU', 'customer_conversion_rate': 1, 'provider': 'Managed Private cloud', 'pc_provider_tax_cost': 0.0, 'default_total_cost': 0.0, 'provider_final_bill_flag': 0, 'default_currency': 'unknown'}, 'cost_prefix': 'C_', 'columns': {'customerConversionRate': None, 'orderId': None, 'serviceEndDate': None, 'providerRecordId': 'Date', 'description': None, 'tags': 'Tags', 'assetAccountId': 'SubscriptionGuid', 'customerCurrencyDate': None, 'providerCurrency': None, 'billingAccountId': None, 'period': None, 'unitOfMeasure': 'Unit Of Measure', 'pcProviderTaxCost': None, 'pcCustomerTotalCost': None, 'providerName': None, 'providerRegion': 'Resource Location', 'pcProviderTotalCost': 'ExtendedCost', 'assetParentId': None, 'extractDate': None, 'providerAssetId': 'Instance ID', 'providerInvoiceId': None, 'customerCurrency': None, 'pcCustomerUnitCost': None, 'pcProviderUnitCost': 'ResourceRate', 'serviceStartDate': None, 'providerServiceDescription': None, 'invoiceEndDate': None, 'assetName': None, 'providerFinalBillFlag': None, 'quantity': 'Consumed Quantity', 'invoiceStartDate': None}, 'gpdfileformat': 'C_{}_{}.{}'}
config = {'vmware': {'enablerotatinglog': True, 'logging': {'loggers': {'vmware.extract': {'level': 'INFO', 'propagate': False, 'handlers': ['console']}}, 'version': 1, 'root': {'level': 'INFO', 'handlers': ['console']}, 'formatters': {'default': {'format': '%(asctime)s  %(levelname)-5.5s  [%(threadName)s][%(name)s] %(message)s'}}, 'handlers': {'rotating': {'delay': True, 'backupCount': 5, 'level': 'INFO', 'maxBytes': 20480000, 'class': 'logging.handlers.RotatingFileHandler', 'filename': 'tmpfile'}, 'console': {'formatter': 'default', 'class': 'logging.StreamHandler', 'stream': 'ext://sys.stdout', 'level': 'INFO'}}}, 'broker': {'queue': 'vmware.extract'}, 'deletetempfiles': True}}
rate_card_config = {'type': 'flat', 'rate_card': {'vsphere.local':'abc.json','cloudmatrix.local':'xyz.json'}}
rate_card_config1 = {'type': 'complex', 'rate_card': {'vsphere.local':'abc.json','cloudmatrix.local':'xyz.json'}}
rate_card_config2 = {'type': 'custom', 'rate_card': {'vsphere.local':'abc.json','cloudmatrix.local':'xyz.json'}}


"""
    Mocks several functions from cost/client.py
"""

class Mock_SI:

    def __init__(self, vserver, user_name, password):
        self.vserver = vserver
        self.user_name = user_name
        self.password = password


class Properties():
    reply_to = 'reply_to'
    correlation_id = 'correlation_id'


class MockCost:

    logger = logging.getLogger('{}'.format(
        __name__
    ))

    @staticmethod
    def mock_si(*args, **kwargs):
        si = Mock_SI()
        return si

    @staticmethod
    def mock_load_yaml(*args, **kwargs):
        return settings

    @staticmethod
    def mock_load(*args, **kwargs):
        return config

    @staticmethod
    def mock_load_rate_card_config(*args, **kwargs):
        return rate_card_config

    @staticmethod
    def mock_load_rate_card_config_for_complex_type(*args, **kwargs):
        return rate_card_config1

    @staticmethod
    def mock_load_rate_card_config1(*args, **kwargs):
        return rate_card_config2

    @staticmethod
    def mock_publish_progress(*args, **kwargs):
        pass

    @staticmethod
    def mocked_path(*args, **kwargs):
        for arg in args:
            print "another arg:", arg
        return Path(*args)

    @staticmethod
    def mocked_rmtree(*args, **kwargs):
        pass

    @staticmethod
    def mocked_publish_message_exception(*args, **kwargs):
        raise Exception("Publish failed")

    @staticmethod
    def mock_basic_publish_exception(*args, **kwargs):
        raise Exception("Publish failed")

    @staticmethod
    def mock_exception(*args, **kwargs):
        raise Exception("Mocked Exception")

    @staticmethod
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, content, status_code):
                self.json_data = json_data
                self.content = content
                self.status_code = status_code

            def json(selft):
                return {"description":"Invalid Request"}

        if "identity/api/tokens" in args[0]:
            return MockResponse({"content":{"description": "Invalid request"}},
                                {"json":{"description":"Invalid Request"}},400)

    @staticmethod
    def mocked_requests_get1(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, content, status_code):
                self.json_data = json_data
                self.content = content
                self.status_code = status_code

            def json(selft):
                return {"description": "Invalid Request"}

        if "identity/api/tokens" in args[0]:
            return MockResponse({"content": {}},
                                {"json": {}}, None)
