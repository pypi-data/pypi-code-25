"""
Python SDK for PixelHosting.
"""
import json
import requests


class PixelHosting():
    def __init__(self, api_key, api_key_id):
        self.api_key = api_key
        self.api_key_id = api_key_id

    def upload(self, data):
        """
        Uploads an image to PixelHosting and returns JSON.
        """

        payload = {"data": data}
        headers = {
            "x-api-key": self.api_key,
            "x-api-key-id": self.api_key_id,
            "content-type": "application/json"
        }

        request = requests.post("https://api.pixelhosting.co/upload",
                                json=payload, headers=headers)

        try:
            return request.json()
        except json.decoder.JSONDecodeError:
            return {"error": request.content}
