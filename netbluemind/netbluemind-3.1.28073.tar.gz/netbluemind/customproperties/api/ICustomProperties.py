#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

ICustomProperties_VERSION = "3.1.0.qualifier"

class ICustomProperties(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/customproperties'

	def get (self, objectName ):
		postUri = "/{objectName}";
		__data__ = None
		postUri = postUri.replace("{objectName}",objectName);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ICustomProperties_VERSION}, data = json.dumps(__data__));
		from netbluemind.customproperties.api.CustomPropertiesRequirements import CustomPropertiesRequirements
		from netbluemind.customproperties.api.CustomPropertiesRequirements import __CustomPropertiesRequirementsSerDer__
		return self.handleResult__(__CustomPropertiesRequirementsSerDer__(), response)
