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

class CustomPropertiesRequirements :
	def __init__( self):
		self.support = None
		self.requesterId = None
		self.customProperties = None
		pass

class __CustomPropertiesRequirementsSerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = CustomPropertiesRequirements()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		supportValue = value['support']
		instance.support = serder.STRING.parse(supportValue)
		requesterIdValue = value['requesterId']
		instance.requesterId = serder.STRING.parse(requesterIdValue)
		from netbluemind.customproperties.api.CustomProperty import CustomProperty
		from netbluemind.customproperties.api.CustomProperty import __CustomPropertySerDer__
		customPropertiesValue = value['customProperties']
		instance.customProperties = serder.CollectionSerDer(__CustomPropertySerDer__()).parse(customPropertiesValue)
		return instance

	def encode(self, value):
		if(value == None):
			return None
		instance = dict()
		self.encodeInternal(value,instance)
		return instance

	def encodeInternal(self, value, instance):

		supportValue = value.support
		instance["support"] = serder.STRING.encode(supportValue)
		requesterIdValue = value.requesterId
		instance["requesterId"] = serder.STRING.encode(requesterIdValue)
		from netbluemind.customproperties.api.CustomProperty import CustomProperty
		from netbluemind.customproperties.api.CustomProperty import __CustomPropertySerDer__
		customPropertiesValue = value.customProperties
		instance["customProperties"] = serder.CollectionSerDer(__CustomPropertySerDer__()).encode(customPropertiesValue)
		return instance

