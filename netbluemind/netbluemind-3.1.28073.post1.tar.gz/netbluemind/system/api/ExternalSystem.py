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
from netbluemind.python import serder

class ExternalSystem :
	def __init__( self):
		self.identifier = None
		self.description = None
		self.authKind = None
		pass

class __ExternalSystemSerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = ExternalSystem()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		identifierValue = value['identifier']
		instance.identifier = serder.STRING.parse(identifierValue)
		descriptionValue = value['description']
		instance.description = serder.STRING.parse(descriptionValue)
		from netbluemind.system.api.ExternalSystemAuthKind import ExternalSystemAuthKind
		from netbluemind.system.api.ExternalSystemAuthKind import __ExternalSystemAuthKindSerDer__
		authKindValue = value['authKind']
		instance.authKind = __ExternalSystemAuthKindSerDer__().parse(authKindValue)
		return instance

	def encode(self, value):
		if(value == None):
			return None
		instance = dict()
		self.encodeInternal(value,instance)
		return instance

	def encodeInternal(self, value, instance):

		identifierValue = value.identifier
		instance["identifier"] = serder.STRING.encode(identifierValue)
		descriptionValue = value.description
		instance["description"] = serder.STRING.encode(descriptionValue)
		from netbluemind.system.api.ExternalSystemAuthKind import ExternalSystemAuthKind
		from netbluemind.system.api.ExternalSystemAuthKind import __ExternalSystemAuthKindSerDer__
		authKindValue = value.authKind
		instance["authKind"] = __ExternalSystemAuthKindSerDer__().encode(authKindValue)
		return instance

