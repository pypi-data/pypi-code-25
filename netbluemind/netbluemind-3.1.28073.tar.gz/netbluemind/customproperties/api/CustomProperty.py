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

class CustomProperty :
	def __init__( self):
		self.name = None
		self.type = None
		self.size = None
		self.defaultValue = None
		self.globalAdminOnly = None
		self.translatedName = None
		pass

class __CustomPropertySerDer__:
	def __init__( self ):
		pass

	def parse(self, value):
		if(value == None):
			return None
		instance = CustomProperty()

		self.parseInternal(value, instance)
		return instance

	def parseInternal(self, value, instance):
		nameValue = value['name']
		instance.name = serder.STRING.parse(nameValue)
		from netbluemind.customproperties.api.CustomPropertyType import CustomPropertyType
		from netbluemind.customproperties.api.CustomPropertyType import __CustomPropertyTypeSerDer__
		typeValue = value['type']
		instance.type = __CustomPropertyTypeSerDer__().parse(typeValue)
		sizeValue = value['size']
		instance.size = serder.INT.parse(sizeValue)
		defaultValueValue = value['defaultValue']
		instance.defaultValue = serder.STRING.parse(defaultValueValue)
		globalAdminOnlyValue = value['globalAdminOnly']
		instance.globalAdminOnly = serder.BOOLEAN.parse(globalAdminOnlyValue)
		translatedNameValue = value['translatedName']
		instance.translatedName = serder.MapSerDer(serder.STRING).parse(translatedNameValue)
		return instance

	def encode(self, value):
		if(value == None):
			return None
		instance = dict()
		self.encodeInternal(value,instance)
		return instance

	def encodeInternal(self, value, instance):

		nameValue = value.name
		instance["name"] = serder.STRING.encode(nameValue)
		from netbluemind.customproperties.api.CustomPropertyType import CustomPropertyType
		from netbluemind.customproperties.api.CustomPropertyType import __CustomPropertyTypeSerDer__
		typeValue = value.type
		instance["type"] = __CustomPropertyTypeSerDer__().encode(typeValue)
		sizeValue = value.size
		instance["size"] = serder.INT.encode(sizeValue)
		defaultValueValue = value.defaultValue
		instance["defaultValue"] = serder.STRING.encode(defaultValueValue)
		globalAdminOnlyValue = value.globalAdminOnly
		instance["globalAdminOnly"] = serder.BOOLEAN.encode(globalAdminOnlyValue)
		translatedNameValue = value.translatedName
		instance["translatedName"] = serder.MapSerDer(serder.STRING).encode(translatedNameValue)
		return instance

