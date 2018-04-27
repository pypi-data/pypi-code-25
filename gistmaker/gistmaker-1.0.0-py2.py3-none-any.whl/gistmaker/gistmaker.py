import requests
import json

class GistMaker():
    def __init__(self, api_token):
        self.GITHUB_API = "https://api.github.com"
        self.API_TOKEN = api_token
        self.request_url = "{}/gists".format(self.GITHUB_API)

    def make(self, description, public, content, name):
        headers = {'Authorization': 'token {}'.format(self.API_TOKEN)}
        params = {'scope': 'gist'}
        payload = {
            "description": description,
            "public": public,
            "files": {
                name: {
                    "content": content
                }
            }
        }

        gist_creation = requests.post(self.request_url,headers=headers,params=params,data=json.dumps(payload))

        return gist_creation.json()
