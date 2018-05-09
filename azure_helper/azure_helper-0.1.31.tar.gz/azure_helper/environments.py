import os
import yaml
from azure_helper.apim import Apim

apims = {}

path = os.environ["AZURE_HELPER_ENVIRONMENTS_PATH"]
stream = open(path, "r")
data = yaml.load(stream)

for region in data:
    apims.setdefault(region, {})
    for env, config in data[region].items():
        # Load config values to variables
        apimBaseUrl = config['apimBaseUrl']
        apimId = config['apimId']
        apimKey = config['apimKey']
        pcfWebApiUrl = config['pcfWebApiUrl']
        # Create Apim object for api
        api = Apim(apimBaseUrl, apimId, apimKey, pcfWebApiUrl)
        # Load new api into apims dict
        apims[region].setdefault(env, api)