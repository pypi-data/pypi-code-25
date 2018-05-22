# -*- coding: utf-8 -*-

"""
    tests.controllers.test_webhooks_controller

    This file was automatically generated for MessageMedia by APIMATIC v2.0 ( https://apimatic.io ).
"""

import jsonpickle
import dateutil.parser
from .controller_test_base import ControllerTestBase
from ..test_helper import TestHelper
from message_media_webhooks.api_helper import APIHelper
from message_media_webhooks.models.update_webhook_request import UpdateWebhookRequest


class WebhooksControllerTests(ControllerTestBase):

    @classmethod
    def setUpClass(cls):
        super(WebhooksControllerTests, cls).setUpClass()
        cls.controller = cls.api_client.webhooks

    # Delete a webhook that was previously created for the connected account.
    #A webhook can be cancelled by appending the UUID of the webhook to the endpoint and submitting a DELETE request to the /webhooks/messages endpoint.
    #*Note: Only pre-created webhooks can be deleted. If an invalid or non existent webhook ID parameter is specified in the request, then a HTTP 404 Not Found response will be returned.*
    def test_delete_webhook_1(self):
        # Parameters for the API call
        webhook_id = 'a7f11bb0-f299-4861-a5ca-9b29d04bc5ad'

        # Perform the API call through the SDK function
        self.controller.delete_webhook(webhook_id)

        # Test response code
        self.assertEquals(self.response_catcher.response.status_code, 204)

    # Update a webhook. You can update individual attributes or all of them by submitting a PATCH request to the /webhooks/messages endpoint (the same endpoint used above to delete a webhook)
    #A successful request to the retrieve webhook endpoint will return a response body as follows:
    #```
    #{
    #    "url": "https://webhook.com",
    #    "method": "POST",
    #    "id": "04442623-0961-464e-9cbc-ec50804e0413",
    #    "encoding": "JSON",
    #    "events": [
    #        "RECEIVED_SMS"
    #    ],
    #    "headers": {},
    #    "template": "{\"id\":\"$mtId\", \"status\":\"$statusCode\"}"
    #}
    #```
    #*Note: Only pre-created webhooks can be deleted. If an invalid or non existent webhook ID parameter is specified in the request, then a HTTP 404 Not Found response will be returned.*
    def test_update_webhook_1(self):
        # Parameters for the API call
        webhook_id = 'a7f11bb0-f299-4861-a5ca-9b29d04bc5ad'
        body = APIHelper.json_deserialize((
            '{"url":"https://myurl.com","method":"POST","encoding":"FORM_ENCODED","event'
            's":["ENROUTE_DR"],"template":"{\"id\":\"$mtId\", \"status\":\"$statusCode\"'
            '}"}'
            ), UpdateWebhookRequest.from_dictionary)

        # Perform the API call through the SDK function
        result = self.controller.update_webhook(webhook_id, body)

        # Test response code
        self.assertEquals(self.response_catcher.response.status_code, 200)

