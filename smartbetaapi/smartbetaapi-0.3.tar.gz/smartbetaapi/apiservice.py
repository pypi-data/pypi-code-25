import requests
import datetime
import dateutil.parser
from marshmallow import Schema, ValidationError


from .universecontextmodel import UniverseContextModel
from .universequeryitemmodel import UniverseQueryItemModel
from .universecontextmodelschema import UniverseContextModelSchema
from .universequeryitemmodelschema import UniverseQueryItemModelSchema
from .queryitemschema import QueryItemSchema
from .measurequeryitemschema import MeasureQueryItemSchema
from .attributequeryitemschema import AttributeQueryItemSchema
from .strategyschema import StrategySchema
from .queryitem import QueryItem
from .attributeschema import AttributeSchema
from .enums import QueryItemType
from .smartbetaexception import SmartBetaServerException
from .entityschema import EntitySchema
from .universebystrategymodel import UniverseByStrategyModel
from .universebystrategymodelschema import UniverseByStrategyModelSchema


class APIService:

    def __init__(self, service_url, certificate_path, proxies=[], proxy_auth=None):
        """The APIService class is used to connect to the server side SmartBeta API web service.

        This class is passed as a reference to UniverseContext and Universe classes so that they
        can query the back end web service. There are also a number of class methods that the client may use
        to query the metadata set up in the system.

        Any web calls involving https://xxx.intramundi.com will need the Amundi certificates (Root CA and
        intermediate CA) installed. The certificate_path for the APIService is the local path
        to the file: ca-bundle.crt

        This cert must first be downloaded to your desktop and is available in the cert
        bundle at https://git.intramundi.com/qoa/ktcheck/repository/archive.zip?ref=master

        Args:
            service_url : URL of the web service to query.
            certificate_path:  Local machine path to ca-bundle.crt

        """
        self._serviceURL = service_url
        self._header = {'Content-type': 'application/json-patch+json', 'Accept': 'application/json'}
        self._certPath=certificate_path
        self._proxies = proxies
        self._proxy_auth = proxy_auth

    def get_universe(self, model_to_send: UniverseContextModel) -> []:
        model_schema = UniverseContextModelSchema()
        entity_ids = self._get_data_with_post('/UniverseContext/GetUniverse', model_to_send, model_schema)
        return entity_ids

    def get_data_by_query_item(self, entity_ids: [], query_items: [], active_date: datetime)->[]:
        model_to_send = UniverseQueryItemModel(entity_ids=entity_ids, query_items=query_items, active_date=active_date)
        model_schema = UniverseQueryItemModelSchema()
        my_data = self._get_data_with_post('/Universe/GetData', model_to_send, model_schema)
        return my_data

    def _get_data_with_post(self, url: str, model_to_post, model_schema) -> []:
        try:
            model_json = model_schema.dump(model_to_post)
        except ValidationError as err:
           raise Exception("ERROR: unable to serialise model: " + err.messages)
        if len(self._proxies) > 0:
            response = requests.post(self._serviceURL + url, json=model_json, headers=self._header, proxies=self._proxies,
                                     verify=self._certPath, auth=self._proxy_auth)
        else:
            response = requests.post(self._serviceURL + url, json=model_json, headers=self._header,  verify=self._certPath)
        if response.status_code == requests.codes.ok:
            data = response.json()
        elif response.status_code in [requests.codes.bad_request, requests.codes.bad,
                                      requests.codes.internal_server_error,
                                      requests.codes.server_error]:
            raise SmartBetaServerException(response.json())
        else:
            raise Exception(response)
        return data

    def _get_data(self, url: str) -> []:

        if len(self._proxies) > 0:
            response = requests.get(self._serviceURL + url, headers=self._header,proxies =self._proxies, verify=self._certPath, auth=self._proxy_auth)
        else:
            response = requests.get(self._serviceURL + url, headers=self._header, verify=self._certPath)
        if response.status_code == requests.codes.ok:
            data = response.json()
        elif response.status_code == requests.codes.no_content:
            data = []            
        elif response.status_code in [requests.codes.bad_request, requests.codes.bad,
                                      requests.codes.internal_server_error,
                                      requests.codes.server_error]:
            raise SmartBetaServerException(response.json())
        else:
            raise Exception(response)
        return data

    def get_data_by_strategy(self, entity_ids:[], strategy: str, active_date: datetime)->[]:
        model_to_send = UniverseByStrategyModel(entity_ids=entity_ids, strategy=strategy, active_date=active_date)
        model_schema = UniverseByStrategyModelSchema()
        my_data = self._get_data_with_post('/Universe/GetDataByStrategy', model_to_send, model_schema)
        return my_data

    def get_all_parent_entities(self )->[]:
        """Get a list of all the parent entities set up in the system

        Returns:
            List of Indexes and Portfolios set up in the system.
        """
        jsonData = self._get_data('/Entity/GetAllParents')
        e_schema = EntitySchema(many=True)
        try:
            result = e_schema.load(jsonData)
        except ValidationError as err:
            raise Exception("ERROR: unable to deserialise response:" + err.messages)

        return result

    def get_all_query_items(self)->[]:
        """Get a list of all the query items set up in the system

        Returns:
            List of QueryItems
        """
        jsonData = self._get_data('/QueryItem/GetAll')
        qi_schema = QueryItemSchema(many=True)
        try:
            result = qi_schema.load(jsonData)
        except ValidationError as err:
            raise Exception("ERROR: unable to deserialise response:" + err.messages)

        return result

    def get_attribute_query_item_values(self, queryItemKey: str)->[]:
        """Get the list of valid values that below to an attribute QueryItem

        This is useful when creating an AttributeFilter. It gives the list of valid values to
        use in the filter for the attribute.

        Returns:
            List of string values
        """
        jsonData = self._get_data('/QueryItem/GetAtributeValues/' + queryItemKey)
        att_schema = AttributeSchema(many=True)
        try:
            result = att_schema.load(jsonData)
        except ValidationError as err:
            raise Exception("ERROR: unable to deserialise response:" + err.messages)

        return result

    def get_all_strategies(self)->[]:
        """Get the list of the strategies set up in the system

        Returns:
            List of strategies
        """
        jsonData = self._get_data('/Strategy/GetAllStrategies')
        s_schema = StrategySchema(many=True)
        try:
            result = s_schema.load(jsonData)
        except ValidationError as err:
            raise Exception("ERROR: unable to deserialise response:" + err.messages)

        return result

    def get_query_item_keys_for_strategy(self, strategyName: str)->[]:
        """Get the QueryItems configured for the given strategy

        Returns:
            List of QueryItems
        """
        jsonData = self._get_data('/Strategy/GetQueryItemKeysForStrategy/' + strategyName)

        return jsonData

    def get_latest_active_date(self)->datetime.date:
        """Get the latest active date in the system

        This returns the latest active date in the EntityMeasure table.
        This is the date that is used by default in queries if no active date is specified

        Returns:
            Lastest active date
        """
        jsonData = self._get_data('/Metadata/GetLatestActiveDate')
        returnDate = dateutil.parser.parse(jsonData)
        return returnDate

    def get_measure_query_item_details(self, queryItemKey: str)->[]:
        """Get additional information on a measure QueryItem

        Returns:
            Measure QueryItem details
        """
        jsonData = self._get_data('/QueryItem/GetMeasureDetail/' + queryItemKey)
        measure_schema = MeasureQueryItemSchema()
        try:
            result = measure_schema.load(jsonData)
        except ValidationError as err:
            raise Exception("ERROR: unable to deserialise response:" + err.messages)

        return result

    def get_attribute_query_item_details(self, queryItemKey: str)->[]:
        """Get additional information on an attribute QueryItem

        Returns:
            Attribute QueryItem details
        """
        jsonData = self._get_data('/QueryItem/GetAtributeDetail/' + queryItemKey)
        
        if(len(jsonData) == 0):
            return jsonData   # empty
        else:
            attribute_schema = AttributeQueryItemSchema()
            try:
                result = attribute_schema.load(jsonData)
            except ValidationError as err:
                raise Exception("ERROR: unable to deserialise response:" + err.messages)
            return result

    def save_checkpoint(self, execution_id: str, checkpoint_name: str, data_json=str):
        url = '/Checkpoint/' + execution_id + '/' + checkpoint_name

        if len(self._proxies) > 0:
            response = requests.post( self._serviceURL + url, json=data_json, headers=self._header, proxies=self._proxies,
                                     verify=self._certPath, auth=self._proxy_auth  )
        else:
            response = requests.post(self._serviceURL + url, json=data_json, headers=self._header,
                                     verify=self._certPath)

        if response.status_code == requests.codes.ok:
            return
        elif response.status_code in [requests.codes.bad_request, requests.codes.bad,
                                      requests.codes.internal_server_error,
                                      requests.codes.server_error]:
            raise SmartBetaServerException(response.json())
        else:
            raise Exception(response)
        return


    def get_checkpoint(self, execution_id: str, checkpoint_name: str):
        url = '/Checkpoint/' + execution_id + '/' + checkpoint_name

        jsonData = self._get_data(url)

        return jsonData
