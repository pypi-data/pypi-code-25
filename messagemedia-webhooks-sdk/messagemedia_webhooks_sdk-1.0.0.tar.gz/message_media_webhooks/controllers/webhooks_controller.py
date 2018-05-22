# -*- coding: utf-8 -*-

"""
    message_media_webhooks.controllers.webhooks_controller

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io ).
"""

import logging
from .base_controller import BaseController
from ..api_helper import APIHelper
from ..configuration import Configuration
from ..http.auth.basic_auth import BasicAuth
from ..exceptions.create_webhook_400_response_exception import CreateWebhook400ResponseException
from ..exceptions.retrieve_webhook_400_response_exception import RetrieveWebhook400ResponseException
from ..exceptions.api_exception import APIException
from ..exceptions.update_webhook_400_response_exception import UpdateWebhook400ResponseException

class WebhooksController(BaseController):

    """A Controller to access Endpoints in the message_media_webhooks API."""

    def __init__(self, client=None, call_back=None):
        super(WebhooksController, self).__init__(client, call_back)
        self.logger = logging.getLogger(__name__)

    def create_webhook(self,
                       body):
        """Does a POST request to /v1/webhooks/messages.

        Create a webhook for one or more of the specified events.
        A webhook would typically have the following structure:
        ```
        {
          "url": "http://webhook.com",
          "method": "POST",
          "encoding": "JSON",
          "headers": {
            "Account": "DeveloperPortal7000"
          },
          "events": [
            "RECEIVED_SMS"
          ],
          "template": "{\"id\":\"$mtId\",\"status\":\"$statusCode\"}"
        }
        ```
        A valid webhook must consist of the following properties:
        - ```url``` The configured URL which will trigger the webhook when a
        selected event occurs.
        - ```method``` The methods to map CRUD (create, retrieve, update,
        delete) operations to HTTP requests.
        - ```encoding``` The format in which the payload will be returned. You
        can choose from ```JSON```, ```FORM_ENCODED``` or ```XML```. This will
        automatically add the Content-Type header for you so you don't have to
        add it again in the `headers` property.
        - ```headers``` HTTP header fields which provide required information
        about the request or response, or about the object sent in the message
        body. This should not include the `Content-Type` header.
        - ```events``` Event or events that will trigger the webhook. Atleast
        one event should be present.
        - ```template``` The structure of the payload that will be returned.
        #### Types of Events
        You can select all of the events (listed below) or combine them in
        whatever way you like but atleast one event must be used. Otherwise,
        the webhook won't be created.
        A webhook will be triggered when any one or more of the events occur:
        + **SMS**
            + `RECEIVED_SMS` Receive an SMS
            + `OPT_OUT_SMS` Opt-out occured
        + **MMS**
            + `RECEIVED_MMS` Receive an MMS
        + **DR (Delivery Reports)**
            + `ENROUTE_DR` Message is enroute
            + `EXPIRED_DR` Message has expired
            + `REJECTED_DR` Message is rejected
            + `FAILED_DR` Message has failed 
            + `DELIVERED_DR` Message is delivered
            + `SUBMITTED_DR` Message is submitted
        #### Template Parameters
        You can choose what to include in the data that will be sent as the
        payload via the Webhook.
        Keep in my mind, you must escape the JSON in the template value (see
        example above).
        The table illustrates a list of all the parameters that can be
        included in the template and which event types it can be applied to.
        | Data  | Parameter Name | Example | Event Type |
        |:--|--|--|--|--|
        | **Service Type**  | $type| `SMS` | `DR` `MO` `MO MMS` |
        | **Message ID**  | $mtId, $messageId|
        `877c19ef-fa2e-4cec-827a-e1df9b5509f7` | `DR` `MO` `MO MMS`|
        | **Delivery Report ID** |$drId, $reportId|
        `01e1fa0a-6e27-4945-9cdb-18644b4de043` | `DR` |
        | **Reply ID**| $moId, $replyId|
        `a175e797-2b54-468b-9850-41a3eab32f74` | `MO` `MO MMS` |
        | **Account ID**  | $accountId| `DeveloperPortal7000` | `DR` `MO` `MO
        MMS` |
        | **Message Timestamp**  | $submittedTimestamp|
        `2016-12-07T08:43:00.850Z` | `DR` `MO` `MO MMS` |
        | **Provider Timestamp**  | $receivedTimestamp|
        `2016-12-07T08:44:00.850Z` | `DR` `MO` `MO MMS` |
        | **Message Status** | $status| `enroute` | `DR` |
        | **Status Code**  | $statusCode| `200` | `DR` |
        | **External Metadata** | $metadata.get('key')| `name` | `DR` `MO` `MO
        MMS` |
        | **Source Address**| $sourceAddress| `+61491570156` | `DR` `MO` `MO
        MMS` |
        | **Destination Address**| $destinationAddress| `+61491593156` | `MO`
        `MO MMS` |
        | **Message Content**| $mtContent, $messageContent| `Hi Derp` | `DR`
        `MO` `MO MMS` |
        | **Reply Content**| $moContent, $replyContent| `Hello Derpina` | `MO`
        `MO MMS` |
        | **Retry Count**| $retryCount| `1` | `DR` `MO` `MO MMS` |
        *Note: A 400 response will be returned if the `url` is invalid, the
        `events`, `encoding` or `method` is null or the `headers` has a
        Content-Type  attribute.*

        Args:
            body (CreateWebhookRequest): TODO: type description here. Example:
                
        Returns:
            mixed: Response from the API. Webhook successfully created

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('create_webhook called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for create_webhook.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/webhooks/messages'
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for create_webhook.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for create_webhook.')
            _request = self.http_client.post(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'create_webhook')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for create_webhook.')
            if _context.response.status_code == 400:
                raise CreateWebhook400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            elif _context.response.status_code == 409:
                raise CreateWebhook400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def retrieve_webhook(self,
                         page=None,
                         page_size=None):
        """Does a GET request to /v1/webhooks/messages/.

        Retrieve all the webhooks created for the connected account.
        A successful request to the retrieve webhook endpoint will return a
        response body as follows:
        ```
        {
            "page": 0,
            "pageSize": 100,
            "pageData": [
                {
                    "url": "https://webhook.com",
                    "method": "POST",
                    "id": "8805c9d8-bef7-41c7-906a-69ede93aa024",
                    "encoding": "JSON",
                    "events": [
                        "RECEIVED_SMS"
                    ],
                    "headers": {},
                    "template": "{\"id\":\"$mtId\",
                    \"status\":\"$statusCode\"}"
                }
            ]
        }
        ```
        *Note: Response 400 is returned when the `page` query parameter is not
        valid or the `pageSize` query parameter is not valid.*

        Args:
            page (int, optional): TODO: type description here. Example: 
            page_size (int, optional): TODO: type description here. Example: 

        Returns:
            mixed: Response from the API. 

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('retrieve_webhook called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for retrieve_webhook.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/webhooks/messages/'
            _query_parameters = {
                'page': page,
                'pageSize': page_size
            }
            _query_builder = APIHelper.append_url_with_query_parameters(_query_builder,
                _query_parameters, Configuration.array_serialization)
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for retrieve_webhook.')
            _headers = {
                'accept': 'application/json'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for retrieve_webhook.')
            _request = self.http_client.get(_query_url, headers=_headers)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'retrieve_webhook')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for retrieve_webhook.')
            if _context.response.status_code == 400:
                raise RetrieveWebhook400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def delete_webhook(self,
                       webhook_id):
        """Does a DELETE request to /v1/webhooks/messages/{webhookId}.

        Delete a webhook that was previously created for the connected
        account.
        A webhook can be cancelled by appending the UUID of the webhook to the
        endpoint and submitting a DELETE request to the /webhooks/messages
        endpoint.
        *Note: Only pre-created webhooks can be deleted. If an invalid or non
        existent webhook ID parameter is specified in the request, then a HTTP
        404 Not Found response will be returned.*

        Args:
            webhook_id (uuid|string): TODO: type description here. Example: 

        Returns:
            void: Response from the API. Webhook deleted successfully

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('delete_webhook called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for delete_webhook.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/webhooks/messages/{webhookId}'
            _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
                'webhookId': webhook_id
            })
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for delete_webhook.')
            _request = self.http_client.delete(_query_url)
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'delete_webhook')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for delete_webhook.')
            if _context.response.status_code == 404:
                raise APIException('', _context)
            self.validate_response(_context)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise

    def update_webhook(self,
                       webhook_id,
                       body):
        """Does a PATCH request to /v1/webhooks/messages/{webhookId}.

        Update a webhook. You can update individual attributes or all of them
        by submitting a PATCH request to the /webhooks/messages endpoint (the
        same endpoint used above to delete a webhook)
        A successful request to the retrieve webhook endpoint will return a
        response body as follows:
        ```
        {
            "url": "https://webhook.com",
            "method": "POST",
            "id": "04442623-0961-464e-9cbc-ec50804e0413",
            "encoding": "JSON",
            "events": [
                "RECEIVED_SMS"
            ],
            "headers": {},
            "template": "{\"id\":\"$mtId\", \"status\":\"$statusCode\"}"
        }
        ```
        *Note: Only pre-created webhooks can be deleted. If an invalid or non
        existent webhook ID parameter is specified in the request, then a HTTP
        404 Not Found response will be returned.*

        Args:
            webhook_id (uuid|string): TODO: type description here. Example: 
            body (UpdateWebhookRequest): TODO: type description here. Example:
                
        Returns:
            mixed: Response from the API. Webhook updated successfully

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        try:
            self.logger.info('update_webhook called.')
    
            # Prepare query URL
            self.logger.info('Preparing query URL for update_webhook.')
            _query_builder = Configuration.base_uri
            _query_builder += '/v1/webhooks/messages/{webhookId}'
            _query_builder = APIHelper.append_url_with_template_parameters(_query_builder, { 
                'webhookId': webhook_id
            })
            _query_url = APIHelper.clean_url(_query_builder)
    
            # Prepare headers
            self.logger.info('Preparing headers for update_webhook.')
            _headers = {
                'accept': 'application/json',
                'content-type': 'application/json; charset=utf-8'
            }
    
            # Prepare and execute request
            self.logger.info('Preparing and executing request for update_webhook.')
            _request = self.http_client.patch(_query_url, headers=_headers, parameters=APIHelper.json_serialize(body))
            BasicAuth.apply(_request)
            _context = self.execute_request(_request, name = 'update_webhook')

            # Endpoint and global error handling using HTTP status codes.
            self.logger.info('Validating response for update_webhook.')
            if _context.response.status_code == 400:
                raise UpdateWebhook400ResponseException('Unexpected error in API call. See HTTP response body for details.', _context)
            elif _context.response.status_code == 404:
                raise APIException('', _context)
            self.validate_response(_context)
    
            # Return appropriate type
            return APIHelper.json_deserialize(_context.response.raw_body)

        except Exception as e:
            self.logger.error(e, exc_info = True)
            raise
